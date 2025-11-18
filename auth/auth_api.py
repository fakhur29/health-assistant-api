from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from shared.database import get_user_by_email, create_user, update_user
import hashlib
import re
from datetime import datetime

router = APIRouter()

# Request/Response Models (Data validation)
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    age: int
    weight: float
    height: int
    gender: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    age: int
    weight: float
    height: int
    gender: str
    bmi: float
    member_since: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user_data: UserResponse = None

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def calculate_bmi(weight: float, height: int) -> float:
    return round(weight / ((height / 100) ** 2), 2)

# API Endpoints
@router.post("/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """Register a new user"""
    
    # Validation checks
    if not is_valid_email(request.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    if request.age < 1 or request.age > 120:
        raise HTTPException(status_code=400, detail="Please enter a valid age")
    
    if request.weight < 1 or request.weight > 300:
        raise HTTPException(status_code=400, detail="Please enter a valid weight")
    
    if request.height < 50 or request.height > 250:
        raise HTTPException(status_code=400, detail="Please enter a valid height")
    
    # Check if user already exists
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Calculate BMI
    bmi = calculate_bmi(request.weight, request.height)
    
    # Create user data
    user_data = {
        "username": request.username,
        "password_hash": hash_password(request.password),
        "email": request.email,
        "age": request.age,
        "weight": request.weight,
        "height": request.height,
        "gender": request.gender,
        "bmi": bmi,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "health_data": {},
        "recommendation_level": "basic"
    }
    
    # Save user
    if create_user(request.email, user_data):
        user_response = UserResponse(
            username=request.username,
            email=request.email,
            age=request.age,
            weight=request.weight,
            height=request.height,
            gender=request.gender,
            bmi=bmi,
            member_since=user_data["created_at"][:10]
        )
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            user_data=user_response
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.post("/login", response_model=AuthResponse)
async def login_user(request: LoginRequest):
    """Login user"""
    
    user_data = get_user_by_email(request.email)
    if not user_data:
        raise HTTPException(status_code=401, detail="Email not found")
    
    # Check password
    if user_data["password_hash"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Update last login
    user_data["last_login"] = datetime.now().isoformat()
    update_user(request.email, user_data)
    
    # Prepare response
    user_response = UserResponse(
        username=user_data["username"],
        email=user_data["email"],
        age=user_data["age"],
        weight=user_data["weight"],
        height=user_data["height"],
        gender=user_data["gender"],
        bmi=user_data["bmi"],
        member_since=user_data["created_at"][:10]
    )
    
    return AuthResponse(
        success=True,
        message="Login successful",
        user_data=user_response
    )

@router.get("/user/{email}")
async def get_user_profile(email: str):
    """Get user profile by email"""
    user_data = get_user_by_email(email)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        username=user_data["username"],
        email=user_data["email"],
        age=user_data["age"],
        weight=user_data["weight"],
        height=user_data["height"],
        gender=user_data["gender"],
        bmi=user_data["bmi"],
        member_since=user_data["created_at"][:10]
    )
