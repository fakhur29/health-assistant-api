from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from shared.database import get_user_by_email, update_user

router = APIRouter()

# Request/Response Models
class HealthScoreRequest(BaseModel):
    email: str
    sleep_hours: float
    sleep_quality: int
    steps: int
    exercise_minutes: int
    activity_level: int
    water_intake: float
    stress_level: int
    meditation_minutes: int = 0

class HealthScoreResponse(BaseModel):
    success: bool
    overall_score: int
    category: str
    detailed_scores: Dict[str, float]
    message: str

# Health Score Calculator (copied from your score.py)
class HealthScoreCalculator:
    def __init__(self):
        self.score_weights = {
            'bmi': 0.3,
            'sleep': 0.25, 
            'activity': 0.25,
            'hydration': 0.1,
            'stress': 0.1
        }
    
    def calculate_bmi_score(self, weight: float, height: int) -> float:
        if height <= 0 or weight <= 0:
            return 0
        
        bmi = weight / ((height / 100) ** 2)
        
        if bmi < 18.5:
            score = max(0, 60 + (bmi - 16) * 10)
        elif bmi <= 24.9:
            score = 100
        elif bmi <= 29.9:
            score = max(0, 100 - (bmi - 24.9) * 8)
        else:
            score = max(0, 60 - (bmi - 30) * 4)
        
        return min(100, score)
    
    def calculate_sleep_score(self, sleep_hours: float, sleep_quality: int) -> float:
        if sleep_hours >= 7 and sleep_hours <= 9:
            hours_score = 100
        elif sleep_hours >= 6 or sleep_hours <= 10:
            hours_score = 80
        elif sleep_hours >= 5 or sleep_hours <= 11:
            hours_score = 60
        else:
            hours_score = 40
        
        quality_score = sleep_quality * 20
        sleep_score = (hours_score * 0.7) + (quality_score * 0.3)
        return min(100, sleep_score)
    
    def calculate_activity_score(self, steps: int, exercise_minutes: int, activity_level: int) -> float:
        if steps >= 10000:
            steps_score = 100
        elif steps >= 8000:
            steps_score = 85
        elif steps >= 6000:
            steps_score = 70
        elif steps >= 4000:
            steps_score = 50
        else:
            steps_score = 30
        
        if exercise_minutes >= 150:
            exercise_score = 100
        elif exercise_minutes >= 120:
            exercise_score = 85
        elif exercise_minutes >= 90:
            exercise_score = 70
        elif exercise_minutes >= 30:
            exercise_score = 50
        else:
            exercise_score = 20
        
        activity_level_score = (activity_level - 1) * 25
        activity_score = (steps_score * 0.4) + (exercise_score * 0.4) + (activity_level_score * 0.2)
        return min(100, activity_score)
    
    def calculate_hydration_score(self, water_intake: float) -> float:
        if water_intake >= 2.5:
            score = 100
        elif water_intake >= 2.0:
            score = 85
        elif water_intake >= 1.5:
            score = 70
        elif water_intake >= 1.0:
            score = 50
        else:
            score = 30
        return score
    
    def calculate_stress_score(self, stress_level: int, meditation_minutes: int) -> float:
        stress_component = (5 - stress_level) * 20
        
        if meditation_minutes >= 20:
            meditation_score = 100
        elif meditation_minutes >= 15:
            meditation_score = 85
        elif meditation_minutes >= 10:
            meditation_score = 70
        elif meditation_minutes >= 5:
            meditation_score = 50
        else:
            meditation_score = 30
        
        stress_score = (stress_component * 0.6) + (meditation_score * 0.4)
        return min(100, stress_score)
    
    def calculate_overall_score(self, user_data: Dict[str, Any], health_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Calculate individual scores
            bmi_score = self.calculate_bmi_score(user_data['weight'], user_data['height'])
            sleep_score = self.calculate_sleep_score(health_data['sleep_hours'], health_data['sleep_quality'])
            activity_score = self.calculate_activity_score(health_data['steps'], health_data['exercise_minutes'], health_data['activity_level'])
            hydration_score = self.calculate_hydration_score(health_data['water_intake'])
            stress_score = self.calculate_stress_score(health_data['stress_level'], health_data['meditation_minutes'])
            
            # Calculate weighted overall score
            overall_score = (
                bmi_score * self.score_weights['bmi'] +
                sleep_score * self.score_weights['sleep'] +
                activity_score * self.score_weights['activity'] +
                hydration_score * self.score_weights['hydration'] +
                stress_score * self.score_weights['stress']
            )
            
            # Get health category
            if overall_score >= 90:
                category = "Excellent"
            elif overall_score >= 80:
                category = "Very Good"
            elif overall_score >= 70:
                category = "Good"
            elif overall_score >= 60:
                category = "Fair"
            else:
                category = "Needs Improvement"
            
            return {
                'overall_score': round(overall_score),
                'category': category,
                'detailed_scores': {
                    'bmi_score': round(bmi_score),
                    'sleep_score': round(sleep_score),
                    'activity_score': round(activity_score),
                    'hydration_score': round(hydration_score),
                    'stress_score': round(stress_score)
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# API Endpoints
calculator = HealthScoreCalculator()

@router.post("/calculate", response_model=HealthScoreResponse)
async def calculate_health_score(request: HealthScoreRequest):
    """Calculate health score and save to user profile"""
    
    # Validate inputs
    if request.sleep_hours <= 0:
        raise HTTPException(status_code=400, detail="Please enter valid sleep hours")
    if request.steps < 0:
        raise HTTPException(status_code=400, detail="Please enter valid step count")
    if request.exercise_minutes < 0:
        raise HTTPException(status_code=400, detail="Please enter valid exercise minutes")
    if request.water_intake < 0:
        raise HTTPException(status_code=400, detail="Please enter valid water intake")
    if request.sleep_quality < 1 or request.sleep_quality > 5:
        raise HTTPException(status_code=400, detail="Sleep quality must be between 1-5")
    if request.stress_level < 1 or request.stress_level > 5:
        raise HTTPException(status_code=400, detail="Stress level must be between 1-5")
    if request.activity_level < 1 or request.activity_level > 5:
        raise HTTPException(status_code=400, detail="Activity level must be between 1-5")
    
    # Get user data
    user_data = get_user_by_email(request.email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare health data
    health_data = {
        'sleep_hours': request.sleep_hours,
        'sleep_quality': request.sleep_quality,
        'steps': request.steps,
        'exercise_minutes': request.exercise_minutes,
        'activity_level': request.activity_level,
        'water_intake': request.water_intake,
        'stress_level': request.stress_level,
        'meditation_minutes': request.meditation_minutes
    }
    
    # Calculate score
    result = calculator.calculate_overall_score(user_data, health_data)
    
    # Save health data to user profile
    user_health_data = {
        'sleep_score': result['detailed_scores']['sleep_score'],
        'activity_score': result['detailed_scores']['activity_score'],
        'stress_score': result['detailed_scores']['stress_score'],
        'hydration_score': result['detailed_scores']['hydration_score'],
        'bmi_score': result['detailed_scores']['bmi_score'],
        'overall_score': result['overall_score']
    }
    
    # Update user data
    user_data['health_data'] = user_health_data
    user_data['recommendation_level'] = 'advanced'
    
    if update_user(request.email, user_data):
        return HealthScoreResponse(
            success=True,
            overall_score=result['overall_score'],
            category=result['category'],
            detailed_scores=result['detailed_scores'],
            message="Health score calculated and saved successfully!"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to save health data")

@router.get("/user/{email}")
async def get_user_health_data(email: str):
    """Get user's health data"""
    user_data = get_user_by_email(email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "health_data": user_data.get('health_data', {}),
        "recommendation_level": user_data.get('recommendation_level', 'basic')
    }