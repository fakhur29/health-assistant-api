from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter()

# Gemini API Configuration
API_KEY = "AIzaSyAGRyM5kuyXJ0nBu-107KPr2TGkYcjFy38"
MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Simple keyword lists
GREETING_KEYWORDS = ["hi", "hello", "hey", "salam", "assalam", "yo"]
SYMPTOM_KEYWORDS = [
    "fever", "cough", "headache", "pain", "nausea", "vomit", "cold",
    "flu", "sore throat", "infection", "stomach", "diarrhea", "fatigue",
    "dizziness", "rash", "allergy", "breathing", "chest", "temperature"
]

# Request/Response Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    error: str = None

# Helper functions
def detect_greeting(text: str) -> bool:
    text = text.lower()
    return any(greet in text for greet in GREETING_KEYWORDS)

def detect_symptom(text: str) -> bool:
    text = text.lower()
    return any(symptom in text for symptom in SYMPTOM_KEYWORDS)

def build_prompt(user_input: str) -> str:
    """Decides what type of response structure to send to Gemini."""
    
    if detect_greeting(user_input):
        return f"""
You are a friendly health assistant.
User said: "{user_input}"
Reply politely and ask how you can help regarding health.
"""
    elif detect_symptom(user_input):
        return f"""
You are a medical assistant bot.
The user describes: "{user_input}"

Respond ONLY in this structure:

**Possible Causes:** (List 2–3 likely conditions)
**Recommended Actions:** (List practical steps)
**Advice:** (One short general advice)

Keep it short and simple.
"""
    else:
        return f"""
You are a health assistant.
The user says: "{user_input}"
Reply helpfully about health and wellness topics.
"""

# API Endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with AI health assistant"""
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Build final prompt
        full_prompt = build_prompt(request.message)
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        }
        
        body = {
            "contents": [
                {"role": "user", "parts": [{"text": full_prompt}]}
            ]
        }
        
        # Call Gemini API
        response = requests.post(API_URL, headers=headers, json=body)
        
        if response.status_code == 200:
            result = response.json()
            try:
                ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
                return ChatResponse(
                    success=True,
                    response=ai_response
                )
            except (KeyError, IndexError):
                return ChatResponse(
                    success=False,
                    response="",
                    error="Unexpected response format from AI service"
                )
        else:
            return ChatResponse(
                success=False,
                response="",
                error=f"AI service error: {response.status_code}"
            )
            
    except requests.exceptions.RequestException as e:
        return ChatResponse(
            success=False,
            response="",
            error=f"Network error: {str(e)}"
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            response="",
            error=f"Unexpected error: {str(e)}"
        )

@router.get("/test")
async def test_chatbot():
    """Test endpoint to check if chatbot is working"""
    return {
        "status": "Chatbot API is working",
        "endpoints": {
            "chat": "POST /api/chatbot/chat"
        }
    }
