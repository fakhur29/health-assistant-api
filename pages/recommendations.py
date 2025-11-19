import streamlit as st
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
st.set_page_config(
    page_title="Recommendations - Health Assistant", 
    page_icon="🎯"
)
st.title("🎯 Personalized Health Recommendations")
st.markdown("---")

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.warning("🔐 Please login first to get personalized recommendations!")
    st.stop()

st.success(f"Welcome, {st.session_state.user_email}! Get your personalized health plan.")

# Load user data
USERS_FILE = Path(__file__).parent.parent / "users.json"

def load_user_data():
    """Load user data from JSON file"""
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        return {}
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        return {}

def calculate_bmi(weight, height):
    """Calculate BMI from weight and height"""
    height_m = height / 100  # Convert cm to meters
    return round(weight / (height_m * height_m), 1)

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return "Underweight", "weight_gain"
    elif 18.5 <= bmi < 25:
        return "Normal", "maintenance"
    elif 25 <= bmi < 30:
        return "Overweight", "weight_loss"
    else:
        return "Obese", "weight_loss"

# Get user data
users_data = load_user_data()
user_email = st.session_state.user_email

if user_email not in users_data:
    st.error("User data not found! Please register again.")
    st.stop()

user_data = users_data[user_email]

# Check if user has health assessment data
has_health_data = "health_data" in user_data

# Display current user info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Age", user_data["age"])
with col2:
    st.metric("Weight", f"{user_data['weight']} kg")
with col3:
    st.metric("Height", f"{user_data['height']} cm")

# Calculate BMI
bmi = calculate_bmi(user_data["weight"], user_data["height"])
bmi_category, focus_area = get_bmi_category(bmi)

st.metric("BMI", f"{bmi} ({bmi_category})")

# Get Recommendations Button
if st.button("🎯 Get My Recommendations", use_container_width=True):
    with st.spinner("Generating your personalized recommendations..."):
        try:
            # Import recommendation engine
            from recommendations.rec_api import RecommendationEngine
            
            # Prepare user data for recommendations
            user_profile = {
                'age': user_data['age'],
                'weight': user_data['weight'],
                'height': user_data['height'],
                'gender': user_data['gender'],
                'bmi': bmi
            }
            
            # Add health data if available
            if has_health_data:
                user_profile['health_data'] = user_data['health_data']
                plan_level = "ADVANCED"
            else:
                plan_level = "BASIC"
            
            # Get recommendations
            engine = RecommendationEngine()
            recommendations = engine.get_recommendations(user_profile)
            
            # Display recommendations
            st.success("✅ Your Personalized Health Plan is Ready!")
            
            # Level and Focus
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Plan Level", plan_level)
            with col2:
                st.metric("Primary Focus", recommendations['focus'].replace('_', ' ').title())
            
            # Focus Areas
            if 'focus_areas' in recommendations and recommendations['focus_areas']:
                st.subheader("🎯 Focus Areas")
                focus_text = " • ".join([f.replace('_', ' ').title() for f in recommendations['focus_areas']])
                st.info(focus_text)
            
            # Diet Plan
            st.subheader("🍽️ Your Diet Plan")
            diet_lines = recommendations['diet_plan'].split('\n')
            for line in diet_lines:
                if line.strip():
                    st.write(line.strip())
            
            # Workout Plan
            st.subheader("💪 Your Workout Plan")
            workout_lines = recommendations['workout_plan'].split('\n')
            for line in workout_lines:
                if line.strip():
                    st.write(line.strip())
            
            # Lifestyle Tips
            if 'lifestyle_tips' in recommendations and recommendations['lifestyle_tips']:
                st.subheader("🌟 Lifestyle Recommendations")
                for tip in recommendations['lifestyle_tips']:
                    if tip.strip():
                        st.write(tip.strip())
            
            # Health Analysis (only for advanced)
            if has_health_data and 'health_analysis' in recommendations and recommendations['health_analysis']:
                st.subheader("📊 Health Analysis")
                for analysis in recommendations['health_analysis']:
                    if analysis.strip():
                        st.write(analysis.strip())
            
            st.success(recommendations['message'])
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")

# Info about levels
st.markdown("---")
if has_health_data:
    st.success("🎉 You're receiving **ADVANCED** recommendations based on your complete health profile!")
else:
    st.info("""
    **💡 Improve Your Recommendations:**
    - Complete a **Health Assessment** to unlock **ADVANCED** recommendations
    - Advanced plans include detailed health analysis and personalized lifestyle tips
    - Visit the **💪 Health Score** page to get your complete health profile
    """)

# Instructions
st.markdown("---")
st.info("""
**How it works:**
- **Basic:** Uses your BMI, age, and gender for general recommendations
- **Advanced:** Uses your complete health profile for personalized plans
- Recommendations improve as you complete more health assessments
""")
