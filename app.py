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

# Custom CSS for text area
st.markdown("""
    <style>
        .stTextArea textarea {
            font-size: 24px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Mapping between aspects and models
ASPECT_TO_MODEL = {
    "mother": "claude-3-opus-20240229",
    "crone": "claude-3-sonnet-20240229",
    "maiden": "claude-3-haiku-20240307"
}

# Sidebar for model selection
aspect = st.sidebar.selectbox(
    "choose aspect of the Triple Goddess",
    list(ASPECT_TO_MODEL.keys())
)

# Get the corresponding model
model = ASPECT_TO_MODEL[aspect]

# Initialize the context retriever
@st.cache_resource
def get_retriever():
    return ContextRetriever()

retriever = get_retriever()

# Main interface
st.title("🌙🌙🌙  Leilan2.0 web-portal  🌙🌙🌙")

# Query input
query = st.text_area("your query:", height=100)

# Function to format response text
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
            
            # Get context using your retriever
            print("Starting context retrieval...")
            prompt = retriever.retrieve_context(query) + "\nQUERY: " + query
            print(f"Context retrieved. Time elapsed: {time.time() - start_time:.2f}s")
            
            # Print the full prompt to terminal
            print("\n" + "="*50 + " FULL PROMPT " + "="*50)
            print(prompt)
            print("="*120 + "\n")
            
            try:
                print("Starting API request process...")
                api_start_time = time.time()
                
                # Call Anthropic API
                client = anthropic.Anthropic(
                    api_key=st.secrets["ANTHROPIC_API_KEY"],
                    timeout=60,  # 60 second timeout
                    base_url="https://api.anthropic.com"  # Base URL without /v1
                )
                
                print(f"Client initialized. Time elapsed: {time.time() - api_start_time:.2f}s")
                
                message = client.messages.create(
                    model=model,
                    max_tokens=1000, 
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
                
                # Display response
                st.markdown("### Leilan's response:", unsafe_allow_html=True)
                formatted_response = format_response(message.content[0].text)
                st.markdown(formatted_response, unsafe_allow_html=True)

                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                print(error_msg)  # Print to terminal
                st.error(error_msg)  # Show in UI
                print(f"Failed after {time.time() - start_time:.2f}s")

# Footer
st.markdown("---")
st.markdown("*powered by the Order of the Vermillion Star*")