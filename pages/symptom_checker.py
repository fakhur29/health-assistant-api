import streamlit as st
import sys
import os
import requests
# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
st.set_page_config(
    page_title="Symptom Checker - Health Assistant",
    page_icon="🔍"
)
st.title("🔍 Symptom Checker")
st.markdown("---")

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.warning("🔐 Please login first to use the symptom checker!")
    st.stop()

st.success(f"Welcome, {st.session_state.user_email}! Select your symptoms for analysis.")

# Predefined symptoms list (same as your original API)
SYMPTOMS_LIST = [
    "fever", "cough", "headache", "fatigue", "sore throat", 
    "runny nose", "sneezing", "body aches", "chills", "sweating",
    "nausea", "vomiting", "diarrhea", "stomach pain", "loss of appetite",
    "chest pain", "shortness of breath", "dizziness", "weakness",
    "muscle pain", "joint pain", "rash", "itching", "red eyes",
    "ear pain", "sinus pressure", "congestion", "wheezing"
]

st.subheader("🤒 Select Your Symptoms")

# Select multiple symptoms
selected_symptoms = st.multiselect(
    "Choose one or more symptoms:",
    SYMPTOMS_LIST,
    placeholder="Select your symptoms..."
)

# Show selected symptoms
if selected_symptoms:
    st.write("**Selected Symptoms:**", ", ".join(selected_symptoms))

# Analyze button
if st.button("🔍 Analyze Symptoms", use_container_width=True):
    if not selected_symptoms:
        st.error("❌ Please select at least one symptom!")
    else:
        with st.spinner("Analyzing your symptoms with AI..."):
            try:
                # DIRECT GEMINI API CALL (No FastAPI needed)
                symptoms_text = ", ".join(selected_symptoms)
                
                prompt = f"""
                The user is experiencing these symptoms: {symptoms_text}
                
                Please provide a structured medical analysis in this exact format:
                
                **Possible Conditions:**
                - [Condition 1 with brief explanation]
                - [Condition 2 with brief explanation] 
                - [Condition 3 with brief explanation]
                
                **Recommended Care:**
                - [Self-care advice 1]
                - [Self-care advice 2]
                - [Self-care advice 3]
                
                **When to See a Doctor:**
                - [Warning sign 1]
                - [Warning sign 2]
                - [Warning sign 3]
                
                **Disclaimer:** This is not medical advice. Consult a healthcare professional for proper diagnosis.
                
                Keep it concise and easy to understand.
                """
                
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": "AIzaSyAGRyM5kuyXJ0nBu-107KPr2TGkYcjFy38"
                }
                
                body = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}]
                }
                
                API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
                response = requests.post(API_URL, headers=headers, json=body)
                
                if response.status_code == 200:
                    result = response.json()
                    analysis = result["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Display the AI analysis
                    st.success("✅ Analysis Complete!")
                    st.markdown("---")
                    st.markdown(analysis)
                    
                else:
                    st.error(f"❌ AI API Error: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                
# Quick selection buttons
st.markdown("---")
st.subheader("⚡ Common Symptom Groups")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🦠 Flu-like", use_container_width=True):
        st.session_state.preset_symptoms = ["fever", "cough", "headache", "body aches", "fatigue"]
        st.rerun()

with col2:
    if st.button("🤢 Stomach", use_container_width=True):
        st.session_state.preset_symptoms = ["nausea", "vomiting", "diarrhea", "stomach pain", "loss of appetite"]
        st.rerun()

with col3:
    if st.button("🤧 Cold", use_container_width=True):
        st.session_state.preset_symptoms = ["runny nose", "sneezing", "sore throat", "congestion", "headache"]
        st.rerun()

# Apply preset symptoms if selected
if hasattr(st.session_state, 'preset_symptoms'):
    selected_symptoms = st.session_state.preset_symptoms
    del st.session_state.preset_symptoms

# Medical disclaimer
st.markdown("---")
st.warning("""
**⚠️ MEDICAL DISCLAIMER:**
This tool provides general information only and is not a substitute for professional medical advice. 
Always consult a healthcare provider for proper diagnosis and treatment.
""")
