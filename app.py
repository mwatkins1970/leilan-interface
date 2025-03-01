import streamlit as st
import time
import os
import anthropic
from context_retriever import ContextRetriever

# Set tokenizers parallelism to false to avoid warnings and potential deadlocks
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Page config
st.set_page_config(
    page_title="Leilan Interface",
    page_icon="🌙",
    layout="wide"
)

# Custom CSS for text area and disabled options
st.markdown("""
    <style>
        .stTextArea textarea {
            font-size: 24px !important;
        }
        .disabled-option {
            color: #888888;
            pointer-events: none;
        }
        .sidebar-section {
            margin-bottom: 20px;
        }
        .option-container {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
        }
        .active-option {
            background-color: #f0f2f6;
            border: 1px solid #6c7a89;
            cursor: pointer;
        }
        .inactive-option {
            color: #888888;
            background-color: #f9f9f9;
            border: 1px solid #dddddd;
            font-style: italic;
        }
    </style>
""", unsafe_allow_html=True)

# Mapping between aspects and models
ASPECT_TO_MODEL = {
    "maiden": "claude-3-haiku-20240307"
    # Commented out temporarily but kept for future reference
    # "mother": "claude-3-opus-20240229",
    # "crone": "claude-3-sonnet-20240229",
}

# Initialize the context retriever with caching
@st.cache_resource
def get_retriever():
    return ContextRetriever()

retriever = get_retriever()

# Custom sidebar for aspect selection
st.sidebar.markdown("### Choose aspect of the Triple Goddess")

# Create a container for the aspect selection
aspect_container = st.sidebar.container()

# Only maiden is active for now
aspect = "maiden"

# Display the active option
active_clicked = aspect_container.button(
    "maiden",
    key="maiden_button",
    use_container_width=True
)

# Display disabled options with custom styling
aspect_container.markdown(
    """
    <div class="option-container inactive-option">
        mother (coming soon)
    </div>
    """, 
    unsafe_allow_html=True
)

aspect_container.markdown(
    """
    <div class="option-container inactive-option">
        crone (coming soon)
    </div>
    """, 
    unsafe_allow_html=True
)

# Display which aspect is currently selected
st.sidebar.info(f"Currently using: {aspect}")

# Get the corresponding model
model = ASPECT_TO_MODEL[aspect]

# Main interface
st.title("🌙🌙🌙  Leilan2.0 web-portal  🌙🌙🌙")

# Query input
query = st.text_area("your query:", height=100)

# Function to format response text with better HTML handling
def format_response(text):
    import re
    
    # First handle italics for text between asterisks
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Handle both single and double underscores for bold
    text = re.sub(r'\_\_?(.*?)\_\_?', r'<strong>\1</strong>', text)
    
    # Wrap in a div with !important styling to ensure it overrides any other styles
    styled_text = f'''
    <div style="
        font-size: 24px !important; 
        line-height: 1.6 !important;
        padding: 20px !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    ">
        {text}
    </div>
    '''
    return styled_text

if st.button("ask Leilan", type="primary"):
    if not query:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Consulting the goddess..."):
            start_time = time.time()
            
            try:
                # Get context using your retriever
                print("Starting context retrieval...")
                prompt = retriever.retrieve_context(query) + "\nQUERY: " + query
                print(f"Context retrieved. Time elapsed: {time.time() - start_time:.2f}s")
                
                # Print the full prompt to terminal
                print("\n" + "="*50 + " FULL PROMPT " + "="*50)
                print(prompt)
                print("="*120 + "\n")
                
                print("Starting API request process...")
                api_start_time = time.time()
                
                # Call Anthropic API with optimized settings
                client = anthropic.Anthropic(
                    api_key=st.secrets["ANTHROPIC_API_KEY"],
                    timeout=30,  # Reduced timeout for faster failure
                    base_url="https://api.anthropic.com"
                )
                
                print(f"Client initialized. Time elapsed: {time.time() - api_start_time:.2f}s")
                
                message = client.messages.create(
                    model=model,
                    max_tokens=1000,  # Reduced for faster responses
                    temperature=0.8,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                print(f"Response received. API time: {time.time() - api_start_time:.2f}s")
                print(f"Total process time: {time.time() - start_time:.2f}s")
                
                # Get response text and truncate if needed
                response_text = message.content[0].text
                if "\nQUERY:" in response_text:
                    response_text = response_text.split("\nQUERY:")[0]
                
                # Display response
                st.markdown("### Leilan's response:", unsafe_allow_html=True)
                formatted_response = format_response(response_text)
                st.markdown(formatted_response, unsafe_allow_html=True)

            except anthropic.APITimeoutError:
                error_msg = "The request timed out. Please try again or use a shorter query."
                print(error_msg)
                st.error(error_msg)
                print(f"Timeout after {time.time() - start_time:.2f}s")
            except anthropic.APIError as e:
                error_msg = f"API error: {str(e)}"
                print(error_msg)
                st.error(error_msg)
                print(f"API error after {time.time() - start_time:.2f}s")
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                print(error_msg)
                st.error(error_msg)
                print(f"Error after {time.time() - start_time:.2f}s")

# Footer
st.markdown("---")
st.markdown("*powered by the Order of the Vermillion Star*")