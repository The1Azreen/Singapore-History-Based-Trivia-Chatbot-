import streamlit as st
import time
from datetime import datetime
import requests
import json
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import gc

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

# Load the vector store
vector_store_directory = "./chroma_db"
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
vector_store = Chroma(persist_directory=vector_store_directory, embedding=embeddings)

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3.5-mini-instruct")
model = AutoModelForCausalLM.from_pretrained("microsoft/phi-3.5-mini-instruct")

# Define the classifier
questions = [
    # Singapore History-related questions (1)
    "Who was Sir Stamford Raffles?",
    "Tell me about the Japanese Occupation in Singapore.",
    # ... (other questions)
    # Non-history questions (0)
    "How do I cook a steak?",
    "What is the best way to invest in stocks?",
    # ... (other questions)
]
labels = [1] * 48 + [0] * 40
X_train, X_test, y_train, y_test = train_test_split(questions, labels, test_size=0.2, random_state=42)
classifier = make_pipeline(TfidfVectorizer(), MultinomialNB())
classifier.fit(X_train, y_train)

# Function to query the Hugging Face model with RAG
def query_huggingface_model(prompt, max_retries=2):
    api_token = st.secrets["HF_API_TOKEN"]
    API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-3.5-mini-instruct"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True
        }
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                response_json = response.json()
                generated_text = response_json[0].get("generated_text", "")
                if "<|assistant|>" in generated_text:
                    assistant_response = generated_text.split("<|assistant|>")[1].strip()
                    return assistant_response
                else:
                    return generated_text.replace(prompt, "").strip()
            elif response.status_code == 503:
                if attempt < max_retries - 1:
                    time.sleep(15)
                    continue
                else:
                    return "The model is currently initializing. Please try again shortly."
            else:
                return f"Sorry, I encountered an error (Status code: {response.status_code}). Response: {response.text[:100]}... Please try again later."
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(10)
                continue
            else:
                return "The request timed out. Please try again in a moment."
        except Exception as e:
            return f"An error occurred: {str(e)}. Please try again later."
    return "Unable to get a response after multiple attempts. Please try again later."

# Function to handle RAG-based question answering
def rag_ask_question(question, top_k=3):
    prediction = classifier.predict([question])[0]
    if prediction == 0:
        return "I'm sorry, but I can only answer questions related to Singapore's history."
    retrieved_docs = vector_store.similarity_search(question, k=top_k)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    rag_prompt = f"""<|system|>
You are a specialized AI assistant focused on Singapore's history. You have been trained on comprehensive historical resources about Singapore's history, culture, and development.

Here is some relevant information to help answer the user's question:
{context}

Answer the question based on the provided information. If the information is not sufficient to answer the question confidently, acknowledge the limitations. Provide accurate, educational responses that help users better understand Singapore's rich historical narrative, based on documents you have retrieved.
<|user|>
{question}
<|assistant|>
"""
    try:
        assistant_response = query_huggingface_model(rag_prompt)
        user_tag_pos = assistant_response.find("<|user|>")
        if user_tag_pos != -1:
            assistant_response = assistant_response[:user_tag_pos].strip()
        system_tag_pos = assistant_response.find("<|system|>")
        if system_tag_pos != -1:
            assistant_response = assistant_response[:system_tag_pos].strip()
        return assistant_response
    except Exception as e:
        return f"An error occurred: {e}"

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
                        # Query the Hugging Face model using RAG
                        response = rag_ask_question(user_input)
                        
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