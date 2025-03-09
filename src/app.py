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
    css = load_css("styles/main.css")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except Exception as e:
    st.write(f"CSS file not found. Default styling will be used. Error: {e}")

# Function to query the Hugging Face model
def query_huggingface_model(prompt):
    # Get API key from Streamlit secrets (set in Streamlit Cloud)
    api_token = st.secrets["HF_API_TOKEN"]
    
    API_URL = "https://api-inference.huggingface.co/models/unsloth/Phi-3.5-mini-instruct"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Format the prompt for the model
    prompt_with_context = (
        f"You are a helpful assistant specialized in Singapore history. "
        f"Keep your answers factual, informative and focused on Singapore's history. "
        f"<|user|>\n{prompt}\n<|assistant|>"
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
    
    try:
        # Make the API request
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Extract the assistant's response from the model output
            full_response = response.json()[0]["generated_text"]
            
            # Extract just the assistant's reply
            assistant_reply = full_response.split("<|assistant|>")[1].strip()
            return assistant_reply
        else:
            # Handle different error codes
            if response.status_code == 503:
                return "The model is currently busy or loading. Please try again in a moment."
            else:
                return f"Sorry, I encountered an error (Status code: {response.status_code}). Please try again later."
    
    except requests.exceptions.Timeout:
        return "The request timed out. The model might be busy. Please try again in a moment."
    except Exception as e:
        return f"An error occurred: {str(e)}. Please try again later."

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