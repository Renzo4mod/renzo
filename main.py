import os
import replicate
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import database

# Load environment variables
load_dotenv()

app = FastAPI(title="Renzo AI API")

# --- CORS Configuration ---
# This allows your frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class AuthRequest(BaseModel):
    email: str

class GenerateRequest(BaseModel):
    prompt: str
    user_id: int
    style: str = "cinematic"

# --- Routes ---

@app.get("/")
def read_root():
    return {"status": "online", "message": "Renzo Backend Running"}

@app.post("/auth")
def authenticate_user(request: AuthRequest, db: Session = Depends(database.get_db)):
    """Login or Register a user"""
    # Check if user exists
    user = db.query(database.User).filter(database.User.email == request.email).first()
    
    if user:
        return {"status": "logged_in", "user_id": user.id, "email": user.email}
    
    # Create new user if not
    new_user = database.User(email=request.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": "registered", "user_id": new_user.id, "email": new_user.email}

@app.post("/generate")
def generate_track(request: GenerateRequest, db: Session = Depends(database.get_db)):
    """Generate music using AI"""
    user = db.query(database.User).filter(database.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Enhance prompt
    full_prompt = f"{request.style} style, {request.prompt}"
    
    # --- AI Generation ---
    try:
        # Check for API Key
        api_token = os.environ.get("r8_5mbI5DE6n3AICQZVETiAIigzxtn62AI385bvt")
        if not api_token:
            # Return demo audio if no key found
            return {
                "status": "demo_mode",
                "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            }

        # Run the actual AI
        output = replicate.run(
            "meta/musicgen:671ac645ce5e552cc63a54a87eae24be212b9b15a02653e5a34789a8750f8e61",
            input={
                "prompt": full_prompt,
                "model_version": "stereo-large",
                "duration": 10
            }
        )
        
        # Save result to database
        new_song = database.Song(
            owner_id=user.id, 
            prompt=request.prompt, 
            audio_url=output
        )
        db.add(new_song)
        db.commit()

        return {"status": "generated", "audio_url": output}

    except Exception as e:
        print(f"Error: {e}")
        # Fallback if AI fails
        return {
            "status": "error", 
            "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
        }