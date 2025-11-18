from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from shared.database import get_user_by_email

router = APIRouter()

# Response Models
class RecommendationResponse(BaseModel):
    success: bool
    level: str
    focus: str
    focus_areas: List[str] = []
    diet_plan: str
    workout_plan: str
    lifestyle_tips: List[str] = []
    health_analysis: List[str] = []
    message: str

# Recommendation Engine (copied from your recommendation.py)
class RecommendationEngine:
    def get_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        health_data = user_data.get('health_data', {})
        if health_data and any(key in health_data for key in ['sleep_score', 'activity_score', 'stress_score']):
            return self.get_advanced_recommendations(user_data)
        else:
            return self.get_basic_recommendations(user_data)
    
    def get_basic_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        bmi = user_data['bmi']
        age = user_data['age']
        gender = user_data['gender']
        
        if bmi < 18.5:
            focus = "weight_gain"
        elif bmi <= 24.9:
            focus = "maintenance"
        else:
            focus = "weight_loss"
        
        return {
            'level': 'basic',
            'focus': focus,
            'diet_plan': self.get_basic_diet_plan(focus, age, gender),
            'workout_plan': self.get_basic_workout_plan(focus, age, gender),
            'message': 'Complete health assessment for more personalized recommendations!'
        }
    
    def get_basic_diet_plan(self, focus: str, age: int, gender: str) -> str:
        if focus == "weight_loss":
            return """• Reduce daily calories by 500
• Include high-protein foods like chicken and fish
• Avoid processed foods and added sugars
• Eat more vegetables and fruits"""
        elif focus == "weight_gain":
            return """• Add 300 extra calories daily
• Eat protein-rich foods like eggs and nuts
• Include healthy carbs like whole grains
• Have 5-6 small meals throughout the day"""
        else:
            return """• Maintain your current calorie intake
• Eat balanced meals with lean proteins
• Include whole grains and fruits
• Add healthy fats like nuts and avocado"""
    
    def get_basic_workout_plan(self, focus: str, age: int, gender: str) -> str:
        if focus == "weight_loss":
            return """• Cardio: 30-45 minutes, 4-5 times/week
• Strength: Full body, 2-3 times/week
• Activities: Walking, cycling, swimming
• Stay active throughout the day"""
        elif focus == "weight_gain":
            return """• Strength: Heavy weights, 3-4 times/week
• Compound exercises: Squats, deadlifts
• Allow 1-2 days rest between sessions
• Gradually increase weights"""
        else:
            return """• Mixed: Cardio + Strength, 3-4 times/week
• Try different activities for variety
• Maintain a consistent schedule
• Listen to your body and rest when needed"""

    def get_advanced_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        health_data = user_data.get('health_data', {})
        bmi = user_data['bmi']
        age = user_data['age']
        gender = user_data['gender']
        
        if bmi < 18.5:
            base_focus = "weight_gain"
        elif bmi <= 24.9:
            base_focus = "maintenance"
        else:
            base_focus = "weight_loss"
        
        sleep_score = health_data.get('sleep_score', 0)
        activity_score = health_data.get('activity_score', 0)
        stress_score = health_data.get('stress_score', 0)
        hydration_score = health_data.get('hydration_score', 0)
        
        focus_areas = [base_focus]
        if sleep_score < 60:
            focus_areas.append("sleep_improvement")
        if activity_score < 50:
            focus_areas.append("fitness_boost")
        if stress_score < 60:
            focus_areas.append("stress_management")
        if hydration_score < 70:
            focus_areas.append("hydration_focus")
        
        return {
            'level': 'advanced',
            'focus': base_focus,
            'focus_areas': focus_areas,
            'diet_plan': self.get_advanced_diet_plan(base_focus, health_data, age, gender),
            'workout_plan': self.get_advanced_workout_plan(base_focus, health_data, age, gender),
            'lifestyle_tips': self.get_lifestyle_tips(health_data),
            'health_analysis': self.get_health_analysis(health_data),
            'message': '🎯 Advanced personalized recommendations based on your complete health profile!'
        }
    
    def get_advanced_diet_plan(self, base_focus: str, health_data: Dict[str, Any], age: int, gender: str) -> str:
        base_diet = self.get_basic_diet_plan(base_focus, age, gender)
        
        sleep_score = health_data.get('sleep_score', 0)
        activity_score = health_data.get('activity_score', 0)
        stress_score = health_data.get('stress_score', 0)
        hydration_score = health_data.get('hydration_score', 0)
        
        enhancements = []
        
        if sleep_score < 60:
            enhancements.extend([
                "🌙 **Sleep-Enhancing Foods:**",
                "• Dinner: Turkey, bananas, almonds (rich in tryptophan & magnesium)",
                "• Evening: Chamomile tea, warm milk",
                "• Avoid: Caffeine after 2 PM, heavy meals before bed"
            ])
        
        if activity_score > 70:
            enhancements.extend([
                "💪 **Active Lifestyle Nutrition:**", 
                "• Post-workout: Protein shake within 30 minutes",
                "• Recovery: Complex carbs + protein (3:1 ratio)",
                "• Hydration: Electrolyte drinks during long workouts"
            ])
        elif activity_score < 50:
            enhancements.extend([
                "🚶 **Energy Boost Foods:**",
                "• Breakfast: Oatmeal with nuts and fruits",
                "• Snacks: Greek yogurt, apple with peanut butter",
                "• Iron-rich: Spinach, lentils, lean red meat"
            ])
        
        if stress_score < 60:
            enhancements.extend([
                "🧘 **Stress-Reducing Nutrition:**",
                "• Omega-3: Salmon, walnuts, chia seeds",
                "• Magnesium: Dark leafy greens, avocados",
                "• Vitamin C: Citrus fruits, bell peppers",
                "• Avoid: Sugar crashes, excessive caffeine"
            ])
        
        if hydration_score < 70:
            enhancements.extend([
                "💧 **Hydration Strategy:**",
                "• Morning: 500ml water upon waking",
                "• Meals: Glass of water before each meal",
                "• Electrolytes: Coconut water, watermelon",
                "• Track: Use water tracking app"
            ])
        
        if enhancements:
            return base_diet + "\n\n" + "\n".join(enhancements)
        else:
            return base_diet + "\n\n🌟 **Maintenance Tips:**\n• Continue your balanced diet\n• Regular health check-ups\n• Seasonal food variety"
    
    def get_advanced_workout_plan(self, base_focus: str, health_data: Dict[str, Any], age: int, gender: str) -> str:
        base_workout = self.get_basic_workout_plan(base_focus, age, gender)
        
        sleep_score = health_data.get('sleep_score', 0)
        activity_score = health_data.get('activity_score', 0)
        stress_score = health_data.get('stress_score', 0)
        
        enhancements = []
        
        if sleep_score < 60:
            enhancements.extend([
                "🌙 **Sleep-Focused Fitness:**",
                "• Morning: Sunlight exposure + light walk",
                "• Evening: Gentle yoga or stretching",
                "• Avoid: Intense workouts 3 hours before bed",
                "• Ideal workout time: Morning or early afternoon"
            ])
        
        if activity_score < 50:
            enhancements.extend([
                "🚶 **Beginner-Friendly Routine:**",
                "• Start: 15-20 minute sessions, 3 times/week",
                "• Focus: Consistency over intensity",
                "• Progress: Add 5 minutes weekly",
                "• Mix: Walking, bodyweight exercises, swimming"
            ])
        elif activity_score > 80:
            enhancements.extend([
                "🏆 **Advanced Performance:**",
                "• Periodization: Vary intensity weekly",
                "• Recovery: Active recovery days",
                "• Cross-training: Different activities",
                "• Monitor: Heart rate variability"
            ])
        
        if stress_score < 60:
            enhancements.extend([
                "🧘 **Stress-Relief Fitness:**",
                "• Mindful: Yoga, tai chi, nature walks",
                "• Breathing: Box breathing during workouts",
                "• Recovery: Extra rest days when stressed",
                "• Enjoyable: Choose activities you love"
            ])
        
        if enhancements:
            return base_workout + "\n\n" + "\n".join(enhancements)
        else:
            return base_workout
    
    def get_lifestyle_tips(self, health_data: Dict[str, Any]) -> List[str]:
        sleep_score = health_data.get('sleep_score', 0)
        activity_score = health_data.get('activity_score', 0)
        stress_score = health_data.get('stress_score', 0)
        hydration_score = health_data.get('hydration_score', 0)
        
        tips = []
        
        if sleep_score < 70:
            tips.extend([
                "🛌 **Sleep Optimization:**",
                "• Consistent bedtime: Same time every night",
                "• Bedroom: Cool, dark, and quiet",
                "• Routine: 30-minute wind-down before bed",
                "• Digital detox: No screens 1 hour before sleep"
            ])
        
        if activity_score < 60:
            tips.extend([
                "🏃 **Activity Integration:**",
                "• Desk job: Stand every 30 minutes",
                "• Walking meetings: When possible",
                "• Parking: Far from destinations",
                "• TV time: Light exercises during commercials"
            ])
        
        if stress_score < 60:
            tips.extend([
                "🧘 **Stress Management:**",
                "• Morning: 5-minute meditation",
                "• Breaks: Pomodoro technique (25/5)",
                "• Nature: 20-minute daily outdoor time",
                "• Digital: Designated no-phone times"
            ])
        
        if hydration_score < 70:
            tips.extend([
                "💧 **Hydration Habits:**",
                "• Visible: Water bottle always in sight",
                "• Flavored: Infuse with fruits/herbs",
                "• App reminder: Hourly drink alerts",
                "• Food: Water-rich fruits and vegetables"
            ])
        
        return tips
    
    def get_health_analysis(self, health_data: Dict[str, Any]) -> List[str]:
        analysis = []
        
        sleep_score = health_data.get('sleep_score', 0)
        activity_score = health_data.get('activity_score', 0)
        stress_score = health_data.get('stress_score', 0)
        hydration_score = health_data.get('hydration_score', 0)
        overall_score = health_data.get('overall_score', 0)
        
        analysis.append(f"📊 **Health Score Analysis:** {overall_score}/100")
        
        if sleep_score >= 80:
            analysis.append("✅ **Sleep:** Excellent quality and duration")
        elif sleep_score >= 60:
            analysis.append("⚠️ **Sleep:** Good but could be improved")
        else:
            analysis.append("❌ **Sleep:** Needs significant improvement")
        
        if activity_score >= 80:
            analysis.append("✅ **Activity:** Highly active lifestyle")
        elif activity_score >= 60:
            analysis.append("⚠️ **Activity:** Moderately active")
        else:
            analysis.append("❌ **Activity:** Sedentary lifestyle detected")
        
        if stress_score >= 80:
            analysis.append("✅ **Stress:** Well managed")
        elif stress_score >= 60:
            analysis.append("⚠️ **Stress:** Moderate stress levels")
        else:
            analysis.append("❌ **Stress:** High stress detected")
        
        if hydration_score >= 80:
            analysis.append("✅ **Hydration:** Optimal water intake")
        elif hydration_score >= 60:
            analysis.append("⚠️ **Hydration:** Could drink more water")
        else:
            analysis.append("❌ **Hydration:** Significant dehydration risk")
        
        return analysis

# API Endpoints
engine = RecommendationEngine()

@router.get("/user/{email}", response_model=RecommendationResponse)
async def get_recommendations(email: str):
    """Get personalized recommendations for a user"""
    
    user_data = get_user_by_email(email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    recommendations = engine.get_recommendations(user_data)
    
    return RecommendationResponse(
        success=True,
        level=recommendations['level'],
        focus=recommendations['focus'],
        focus_areas=recommendations.get('focus_areas', []),
        diet_plan=recommendations['diet_plan'],
        workout_plan=recommendations['workout_plan'],
        lifestyle_tips=recommendations.get('lifestyle_tips', []),
        health_analysis=recommendations.get('health_analysis', []),
        message=recommendations['message']
    )

@router.get("/test/{email}")
async def test_recommendations(email: str):
    """Test endpoint to check recommendation level"""
    user_data = get_user_by_email(email)
    if not user_data:
        return {"error": "User not found"}
    
    has_health_data = user_data.get('health_data') and any(
        key in user_data['health_data'] for key in ['sleep_score', 'activity_score', 'stress_score']
    )
    
    return {
        "user_exists": True,
        "has_health_data": has_health_data,
        "recommendation_level": user_data.get('recommendation_level', 'basic'),
        "health_data_available": list(user_data.get('health_data', {}).keys())
    }