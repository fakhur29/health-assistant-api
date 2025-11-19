import streamlit as st
import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def load_users():
    """Load users from JSON file"""
    try:
        USERS_FILE = Path(__file__).parent.parent / "users.json"
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        return {}
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        USERS_FILE = Path(__file__).parent.parent / "users.json"
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving users: {e}")
        return False
# Add backend to path
st.set_page_config(
    page_title="Health Score - Health Assistant",
    page_icon="💪"
)
st.title("💪 Health Score Calculator")
st.markdown("---")

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.warning("🔐 Please login first to use the health score calculator!")
    st.stop()

st.success(f"Welcome, {st.session_state.user_email}! Calculate your health score.")

# Health data input form
with st.form("health_score_form"):
    st.subheader("📊 Enter Your Health Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Basic Information**")
        weight = st.number_input("Weight (kg)*", min_value=30.0, max_value=200.0, value=70.0)
        height = st.number_input("Height (cm)*", min_value=100, max_value=250, value=170)
    
    with col2:
        st.write("**Sleep Quality**")
        sleep_hours = st.slider("Sleep Hours*", min_value=0.0, max_value=12.0, value=7.0, step=0.5)
        sleep_quality = st.slider("Sleep Quality (1-5)*", min_value=1, max_value=5, value=3,
                                 help="1 = Poor, 5 = Excellent")
    
    st.write("**Physical Activity**")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        steps = st.number_input("Daily Steps*", min_value=0, max_value=50000, value=8000)
    with col4:
        exercise_minutes = st.number_input("Exercise Minutes*", min_value=0, max_value=300, value=30,
                                         help="Moderate to vigorous exercise")
    with col5:
        activity_level = st.selectbox("Activity Level*", 
                                    [1, 2, 3, 4, 5],
                                    index=2,
                                    format_func=lambda x: {
                                        1: "Sedentary", 
                                        2: "Light", 
                                        3: "Moderate", 
                                        4: "Active", 
                                        5: "Very Active"
                                    }[x])
    
    st.write("**Lifestyle Factors**")
    col6, col7 = st.columns(2)
    
    with col6:
        water_intake = st.slider("Water Intake (Liters)*", min_value=0.0, max_value=5.0, value=2.0, step=0.5)
    with col7:
        stress_level = st.slider("Stress Level (1-5)*", min_value=1, max_value=5, value=3,
                               help="1 = Very Low, 5 = Very High")
        meditation_minutes = st.number_input("Meditation Minutes", min_value=0, max_value=120, value=0)
    
    calculate_btn = st.form_submit_button("Calculate Health Score", use_container_width=True)

# Calculate score when form is submitted
if calculate_btn:
    # Validate inputs
    if weight <= 0 or height <= 0:
        st.error("Please enter valid weight and height!")
    elif sleep_hours <= 0:
        st.error("Please enter valid sleep hours!")
    else:
        with st.spinner("Calculating your health score..."):
            try:
                # Import health score calculator
                from health_score.score_api import HealthScoreCalculator
                
                # Create calculator instance
                calculator = HealthScoreCalculator()
                
                # Calculate individual scores
                bmi_score = calculator.calculate_bmi_score(weight, height)
                sleep_score = calculator.calculate_sleep_score(sleep_hours, sleep_quality)
                activity_score = calculator.calculate_activity_score(steps, exercise_minutes, activity_level)
                hydration_score = calculator.calculate_hydration_score(water_intake)
                stress_score = calculator.calculate_stress_score(stress_level, meditation_minutes)
                
                # Calculate overall score
                overall_score = round(
                    bmi_score * 0.3 +
                    sleep_score * 0.25 +
                    activity_score * 0.25 +
                    hydration_score * 0.1 +
                    stress_score * 0.1
                )
                
                # Determine category
                if overall_score >= 90:
                    category = "Excellent"
                    color = "green"
                    emoji = "🎉"
                elif overall_score >= 80:
                    category = "Very Good"
                    color = "lightgreen"
                    emoji = "👍"
                elif overall_score >= 70:
                    category = "Good"
                    color = "yellow"
                    emoji = "✅"
                elif overall_score >= 60:
                    category = "Fair"
                    color = "orange"
                    emoji = "⚠️"
                else:
                    category = "Needs Improvement"
                    color = "red"
                    emoji = "💪"
                
                # Display results
                st.success("")
                                # Save health data to user profile
                                # Save health data to user profile
                try:
                    user_email = st.session_state.user_email
                    users_data = load_users()
                    if user_email in users_data:
                        # Calculate BMI for saving
                        height_m = height / 100
                        user_bmi = round(weight / (height_m * height_m), 1)
                        
                        users_data[user_email]["health_data"] = {
                            'sleep_score': sleep_score,
                            'activity_score': activity_score,
                            'stress_score': stress_score,
                            'hydration_score': hydration_score,
                            'overall_score': overall_score,
                            'bmi': user_bmi
                        }
                        if save_users(users_data):
                            st.success("💾 Health data saved to your profile!")
                        else:
                            st.error("❌ Failed to save health data")
                except Exception as e:
                    st.error(f"Could not save health data: {e}")

                st.markdown(f"""
                <div style="text-align: center; padding: 30px; border-radius: 15px; background: {color}; color: black; margin: 20px 0;">
                    <h1 style="font-size: 64px; margin: 0; font-weight: bold;">{overall_score}/100</h1>
                    <h2 style="margin: 10px 0; font-size: 32px;">{emoji} {category}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Display detailed scores
                st.subheader("📈 Detailed Breakdown")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("BMI Score", f"{bmi_score}")
                with col2:
                    st.metric("Sleep Score", f"{sleep_score}")
                with col3:
                    st.metric("Activity Score", f"{activity_score}")
                with col4:
                    st.metric("Hydration Score", f"{hydration_score}")
                with col5:
                    st.metric("Stress Score", f"{stress_score}")
                
                # Health tips based on scores
                st.subheader("💡 Health Tips")
                tips = []
                if sleep_score < 60:
                    tips.append("• Improve sleep: Aim for 7-9 hours of quality sleep")
                if activity_score < 50:
                    tips.append("• Increase activity: Try to reach 10,000 steps daily")
                if hydration_score < 70:
                    tips.append("• Drink more water: Aim for 2-3 liters daily")
                if stress_score < 60:
                    tips.append("• Manage stress: Practice meditation or deep breathing")
                
                if tips:
                    for tip in tips:
                        st.write(tip)
                else:
                    st.success("🎉 Great job! Keep maintaining your healthy habits!")
                    
            except Exception as e:
                st.error(f"Error calculating health score: {str(e)}")

# Instructions
st.markdown("---")
st.info("""
**How it works:**
- **BMI (30%):** Weight and height ratio
- **Sleep (25%):** Duration and quality  
- **Activity (25%):** Steps, exercise, and activity level
- **Hydration (10%):** Daily water intake
- **Stress (10%):** Stress level and meditation
""")
