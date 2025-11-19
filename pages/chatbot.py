import streamlit as st
import sys
import os
import requests

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
st.set_page_config(
    page_title="AI Chatbot - Health Assistant", 
    page_icon="🏥"
)
st.title("🏥 AI Health Chatbot")
st.markdown("---")

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.warning("🔐 Please login first to use the chatbot!")
    st.stop()

st.success(f"Welcome, {st.session_state.user_email}! How can I help you today?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your health question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Real AI response with context
    with st.chat_message("assistant"):
        with st.spinner("AI is thinking..."):
            try:
                # Build conversation context
                conversation_history = ""
                for msg in st.session_state.messages[-4:]:  # Last 4 messages
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation_history += f"{role}: {msg['content']}\n"
                
                # IMPROVED PROMPT for medical responses
                context_prompt = f"""
                You are a medical assistant. Use the conversation history below to provide contextual responses.
                
                Conversation History:
                {conversation_history}
                
                Current User Message: "{prompt}"
                
                Provide helpful medical advice in this structure:
                **Assessment:** [Brief assessment]
                **Recommended Actions:** [2-3 practical steps]
                **When to Seek Help:** [1-2 warning signs]
                **Note:** [General advice]
                
                Keep it concise and helpful.
                """
                
                # Direct API call
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": "AIzaSyAGRyM5kuyXJ0nBu-107KPr2TGkYcjFy38"
                }
                body = {
                    "contents": [{"role": "user", "parts": [{"text": context_prompt}]}]
                }
                
                API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
                api_response = requests.post(API_URL, headers=headers, json=body)
                
                if api_response.status_code == 200:
                    result = api_response.json()
                    response = result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    response = "⚠️ AI service is busy. Please try again."
                    
                st.markdown(response)
            except Exception as e:
                response = f"⚠️ AI service temporarily unavailable. Error: {str(e)}"
                st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Clear chat button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Instructions
st.markdown("---")
st.info("💡 **Tips:** Ask about symptoms, health advice, nutrition, exercise, or any health-related questions!")
