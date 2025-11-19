import streamlit as st
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Login - Health Assistant",
    page_icon="🔐",
    layout="centered"
)

# CORRECT Path to users.json - in main API folder
USERS_FILE = Path(__file__).parent.parent / "users.json"

def load_users():
    """Load users from JSON file"""
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # If file is empty
                    return {}
                return json.loads(content)
        # If file doesn't exist, create it
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        return {}
    except json.JSONDecodeError:
        st.error("❌ Users file is corrupted. Creating new one...")
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        return {}
    except Exception as e:
        st.error(f"❌ Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ Error saving users: {e}")
        return False

def register_user(username, email, password, age, weight, height, gender):
    """Register a new user"""
    users = load_users()
    
    # Check if user already exists
    if email in users:
        return False, "User already exists with this email!"
    
    # Add new user
    users[email] = {
        "username": username,
        "password": password,
        "age": age,
        "weight": weight,
        "height": height,
        "gender": gender
    }
    
    if save_users(users):
        return True, "Registration successful!"
    else:
        return False, "Registration failed!"

def login_user(email, password):
    """Login existing user"""
    users = load_users()
    
    # Check if user exists
    if email not in users:
        return False, "User not found! Please register first."
    
    # Check password
    if users[email]["password"] != password:
        return False, "Incorrect password!"
    
    return True, "Login successful!"

# Main Auth UI
st.title("🏥 Health Assistant")
st.markdown("### 🔐 Login to Your Account")
st.markdown("---")

# If already logged in, show dashboard
if st.session_state.get('logged_in'):
    st.success(f"✅ Welcome back, {st.session_state.user_email}!")
    st.info("You are already logged in. Use the sidebar to navigate.")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()
    
    st.stop()

# Tab selection
tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

with tab1:
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        login_email = st.text_input("📧 Email Address", placeholder="your@email.com")
        login_password = st.text_input("🔒 Password", type="password")
        
        login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
        
        if login_btn:
            if not login_email or not login_password:
                st.error("❌ Please fill all fields!")
            else:
                success, message = login_user(login_email, login_password)
                if success:
                    st.success(f"✅ {message}")
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    users_data = load_users()
                    st.session_state.username = users_data[login_email]["username"]
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

with tab2:
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("👤 Username", placeholder="Enter your username")
            email = st.text_input("📧 Email Address", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Create strong password")
            confirm_password = st.text_input("✅ Confirm Password", type="password", placeholder="Re-enter password")
            
        with col2:
            age = st.number_input("🎂 Age", min_value=1, max_value=120, value=25)
            weight = st.number_input("⚖️ Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
            height = st.number_input("📏 Height (cm)", min_value=100, max_value=250, value=170)
            gender = st.selectbox("🚻 Gender", ["Male", "Female", "Other"])
        
        register_btn = st.form_submit_button("✨ Create Account", use_container_width=True)
        
        if register_btn:
            # Validation
            if not all([username, email, password, confirm_password]):
                st.error("❌ Please fill all fields!")
            elif password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif len(password) < 4:
                st.error("❌ Password must be at least 4 characters!")
            else:
                success, message = register_user(username, email, password, age, weight, height, gender)
                if success:
                    st.success(f"✅ {message}")
                    st.info("You can now login with your credentials.")
                else:
                    st.error(f"❌ {message}")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Your AI Health Assistant")
