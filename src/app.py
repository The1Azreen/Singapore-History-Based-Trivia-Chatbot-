import streamlit as st
import time
from datetime import datetime
import requests
import json
import os

# Page configuration
st.set_page_config(
    page_title="Singapore History Chatbot",
    page_icon="💬",
    layout="wide"
)

# Load CSS from external file
def load_css(css_file):
    with open(css_file, "r") as f:
        css = f.read()
    return css

# Load CSS File
try:
    css = load_css("src/styles/main.css")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except Exception as e:
    st.write(f"CSS file not found. Default styling will be used. Error: {e}")

# Function to query the Hugging Face model
# Function to query the Hugging Face model
def query_huggingface_model(prompt, max_retries=2):
    # Get API key from Streamlit secrets (set in Streamlit Cloud)
    api_token = st.secrets["HF_API_TOKEN"]
    
    # Using Microsoft's Phi-2 model which is more reliable on the free tier
    API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-2"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Format the prompt for the Phi-2 model (simpler format)
    prompt_with_context = (
        f"You are a helpful assistant specialized in Singapore history. "
        f"Keep your answers factual, informative and focused on Singapore's history. "
        f"Question: {prompt}\nAnswer:"
    )
    
    # Prepare the payload
    payload = {
        "inputs": prompt_with_context,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    
    # Add retry logic
    for attempt in range(max_retries):
        try:
            # Make the API request
            response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
            
            # Check if the request was successful
            if response.status_code == 200:
                try:
                    # More robust extraction of the generated text
                    response_json = response.json()
                    
                    # Handle different response formats
                    if isinstance(response_json, list) and len(response_json) > 0:
                        # Format for older models
                        generated_text = response_json[0].get("generated_text", "")
                    elif isinstance(response_json, dict):
                        # Format for some newer models
                        generated_text = response_json.get("generated_text", "")
                    else:
                        # Fallback
                        generated_text = str(response_json)
                    
                    # Phi-2 tends to repeat the prompt, attempt to extract just the answer
                    if "Answer:" in generated_text:
                        answer_part = generated_text.split("Answer:", 1)[1].strip()
                        return answer_part
                    else:
                        # If we can't find the format we expect, return the whole response
                        return generated_text.replace(prompt_with_context, "").strip()
                except Exception as e:
                    # If we fail to parse the JSON, return the raw text
                    return f"Response processing error: {str(e)}. Raw response: {response.text[:300]}..."
            
            # If model is loading, wait and retry
            elif response.status_code == 503:
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(10)  # Wait 10 seconds before retrying
                    continue
                else:
                    return "The model is currently busy or loading. Please try again in a moment."
            else:
                # Other error status codes
                return f"Sorry, I encountered an error (Status code: {response.status_code}). Please try again later."
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            else:
                return "The request timed out. The model might be busy. Please try again in a moment."
        except Exception as e:
            return f"An error occurred: {str(e)}. Please try again later."
    
    # If we've exhausted all retries
    return "Unable to get a response after multiple attempts. Please try again later."

# Setup sidebar
with st.sidebar:
    st.title("Singapore History Chatbot")
    
    # Model info
    st.subheader("About")
    st.write("This chatbot uses the Phi-3.5-mini-instruct model hosted on Hugging Face to answer questions about Singapore's history.")
    
    st.divider()
    
    # Add a button to start a new chat
    if st.button("Start New Chat"):
        # Reset messages to initial state
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Singapore History guide. What would you like to know about Singapore's past?", "timestamp": datetime.now().strftime("%H:%M")}
        ]
        st.rerun()
    
    st.divider()
    
    # Tips for users
    st.subheader("Tips")
    st.write("Try asking about:")
    st.write("• The founding of Singapore")
    st.write("• Major historical events")
    st.write("• Cultural heritage")
    st.write("• Singapore's path to independence")

# Set up the main content area
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Title bar
    st.markdown("<div class='title-container'><h1>Singapore History Chatbot</h1></div>", unsafe_allow_html=True)
    
    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your Singapore History guide. What would you like to know about Singapore's past?", "timestamp": datetime.now().strftime("%H:%M")}
        ]

    # Display chat messages
    chat_container = st.container()
    
    # Input area (fixed at bottom)
    input_container = st.container()
    
    # Display chat messages from history
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-container user-container">
                    <div class="message-header">You</div>
                    <div class="timestamp">{message["timestamp"]}</div>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-container bot-container">
                    <div class="message-header">Singapore History Chatbot</div>
                    <div class="timestamp">{message["timestamp"]}</div>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Add some space at the bottom to prevent overlap with input
        st.markdown("<div style='height: 100px'></div>", unsafe_allow_html=True)
    
    # User input area
    with input_container:
        st.markdown("<div class='input-container'>", unsafe_allow_html=True)
        
        # Create a form for the input to prevent automatic reloading
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([6, 1])
            
            with col1:
                user_input = st.text_input("Ask me about Singapore's history...", key="user_input")
            
            with col2:
                submit_button = st.form_submit_button("Send")
            
            if submit_button and user_input:
                # Add user message to chat history
                st.session_state.messages.append(
                    {"role": "user", "content": user_input, "timestamp": datetime.now().strftime("%H:%M")}
                )
                
                # Display typing indicator while waiting for response
                with st.spinner("Thinking..."):
                    try:
                        # Query the Hugging Face model
                        response = query_huggingface_model(user_input)
                        
                        # Add AI response to chat history
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response, "timestamp": datetime.now().strftime("%H:%M")}
                        )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        # Add error message to chat history
                        st.session_state.messages.append(
                            {"role": "assistant", "content": f"Sorry, I encountered an error. Please try again later.", 
                             "timestamp": datetime.now().strftime("%H:%M")}
                        )
                
                # Rerun the app to display the updated chat
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer with information
st.markdown("""
<div style="text-align: center; margin-top: 20px; margin-bottom: 20px; font-size: 12px; color: #888;">
    This is a demonstration project. 
</div>
""", unsafe_allow_html=True)