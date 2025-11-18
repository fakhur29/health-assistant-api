from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import all our API routers (we'll create these next)
from auth.auth_api import router as auth_router
from chatbot.chatbot_api import router as chatbot_router
from health_score.score_api import router as health_score_router
from recommendations.rec_api import router as recommendations_router
from symptom_checker.symptom_api import router as symptom_router

# Create FastAPI app
app = FastAPI(
    title="Health Assistant API",
    description="Backend API for AI-powered Health Assistant Mobile App",
    version="1.0.0"
)

# Add CORS middleware (important for Flutter app to communicate)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - change in production!
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include all API routes
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(health_score_router, prefix="/api/health-score", tags=["Health Score"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(symptom_router, prefix="/api/symptom-checker", tags=["Symptom Checker"])

# Root endpoint
# @app.get("/")
# async def root():
#     return {
#         "message": "Health Assistant API is running!",
#         "version": "1.0.0",
#         "endpoints": {
#             "auth": "/api/auth",
#             "chatbot": "/api/chatbot", 
#             "health_score": "/api/health-score",
#             "recommendations": "/api/recommendations",
#             "symptom_checker": "/api/symptom-checker"
#         }
#     }
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def root():
    # Redirect root URL to the interactive Swagger UI
    return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Health Assistant API"}

# Run the app (for development)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)