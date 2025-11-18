import json
import os
from typing import Dict, Any

# Path to users.json (adjust if needed)
USERS_FILE = "users.json"

def load_users() -> Dict[str, Any]:
    """Load all users from JSON file"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users_data: Dict[str, Any]) -> bool:
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def get_user_by_email(email: str) -> Dict[str, Any]:
    """Get a specific user by email"""
    users = load_users()
    return users.get(email)

def update_user(email: str, user_data: Dict[str, Any]) -> bool:
    """Update a specific user's data"""
    users = load_users()
    if email in users:
        users[email].update(user_data)
        return save_users(users)
    return False

def create_user(email: str, user_data: Dict[str, Any]) -> bool:
    """Create a new user"""
    users = load_users()
    if email in users:
        return False  # User already exists
    users[email] = user_data
    return save_users(users)