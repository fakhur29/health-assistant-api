import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Health Assistant",
    page_icon="🏥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Redirect to login if not authenticated
if not st.session_state.get('logged_in'):
    # Redirect to auth page
    st.switch_page("pages/Auth.py")

# Main app (only visible after login)
st.title("🏥 Health Assistant Dashboard")
st.markdown("---")

# Welcome message
st.success(f"🎉 Welcome back, {st.session_state.get('username', 'User')}!")
st.write("Use the sidebar to navigate between different health features.")

# Sidebar content - NAVIGATION FIRST
st.sidebar.title("🧭 Navigation")
st.sidebar.info("Select a feature from the menu below:")

# User info in sidebar - BELOW NAVIGATION
st.sidebar.markdown("---")
st.sidebar.title("👤 User Profile")
st.sidebar.success(f"Logged in as: **{st.session_state.user_email}**")

# Logout button - AT BOTTOM
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.username = None
    st.rerun()

# Quick stats or overview can go here
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Health Score", "85", "+5")
    
with col2:
    st.metric("Chat Sessions", "12", "+3")
    
with col3:
    st.metric("Symptom Checks", "8", "+2")

# Recent activity or quick actions
st.markdown("### ⚡ Quick Actions")
quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

with quick_col1:
    if st.button("💬 Chat with AI", use_container_width=True):
        st.switch_page("pages/1_🏥_Chatbot.py")

with quick_col2:
    if st.button("💪 Health Score", use_container_width=True):
        st.switch_page("pages/2_💪_Health_Score.py")

with quick_col3:
    if st.button("🔍 Check Symptoms", use_container_width=True):
        st.switch_page("pages/4_🔍_Symptom_Checker.py")

with quick_col4:
    if st.button("🎯 Get Recommendations", use_container_width=True):
        st.switch_page("pages/3_🎯_Recommendations.py")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Your AI Health Assistant")