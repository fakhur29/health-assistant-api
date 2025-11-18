from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests

router = APIRouter()

# Gemini API Configuration
API_KEY = "AIzaSyAGRyM5kuyXJ0nBu-107KPr2TGkYcjFy38"
MODEL = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Request/Response Models
class SymptomCheckRequest(BaseModel):
    symptoms: List[str]

class SymptomCheckResponse(BaseModel):
    success: bool
    analysis: str
    error: str = None

# API Endpoint
@router.post("/analyze", response_model=SymptomCheckResponse)
async def analyze_symptoms(request: SymptomCheckRequest):
    """Analyze symptoms and provide possible conditions and advice"""
    
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Please select at least one symptom")
    
    symptoms_text = ", ".join(request.symptoms)
    
    try:
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
            "x-goog-api-key": API_KEY
        }
        
        body = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ]
        }
        
        # Call Gemini API
        response = requests.post(API_URL, headers=headers, json=body)
        
        if response.status_code == 200:
            result = response.json()
            try:
                analysis_result = result["candidates"][0]["content"]["parts"][0]["text"]
                return SymptomCheckResponse(
                    success=True,
                    analysis=analysis_result
                )
            except (KeyError, IndexError):
                return SymptomCheckResponse(
                    success=False,
                    analysis="",
                    error="Unexpected response format from AI service"
                )
        else:
            return SymptomCheckResponse(
                success=False,
                analysis="",
                error=f"AI service error: {response.status_code}"
            )
            
    except requests.exceptions.RequestException as e:
        return SymptomCheckResponse(
            success=False,
            analysis="",
            error=f"Network error: {str(e)}"
        )
    except Exception as e:
        return SymptomCheckResponse(
            success=False,
            analysis="",
            error=f"Unexpected error: {str(e)}"
        )

@router.get("/symptoms-list")
async def get_symptoms_list():
    """Get the list of available symptoms for selection"""
    symptoms = [
        "Fever", "Headache", "Cough", "Sore throat", "Runny nose",
        "Body aches", "Fatigue", "Nausea", "Vomiting", "Diarrhea",
        "Chest pain", "Shortness of breath", "Dizziness", "Abdominal pain",
        "Joint pain", "Rash", "Itching", "Swelling", "Loss of appetite",
        "Muscle cramps", "Sneezing", "Chills", "Back pain", "Ear pain"
    ]
    
    return {
        "symptoms": symptoms,
        "count": len(symptoms)
    }

@router.get("/test")
async def test_symptom_checker():
    """Test endpoint to check if symptom checker is working"""
    return {
        "status": "Symptom Checker API is working",
        "endpoints": {
            "analyze": "POST /api/symptom-checker/analyze",
            "symptoms_list": "GET /api/symptom-checker/symptoms-list"
        }
    }