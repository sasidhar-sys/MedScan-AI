import io
import base64
import json
from datetime import datetime, timedelta
from typing import Optional, List
import sqlite3
import hashlib
import secrets

import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from torchvision import models, transforms
from PIL import Image

app = FastAPI(title="EsophaScan AI - Authentication & Analysis")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Database setup
def init_database():
    conn = sqlite3.connect('esophascan.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analysis history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            classification TEXT NOT NULL,
            confidence REAL NOT NULL,
            cancer_probability REAL NOT NULL,
            prediction TEXT NOT NULL,
            is_positive BOOLEAN NOT NULL,
            processing_time REAL NOT NULL,
            image_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Sessions table for auth tokens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# Pydantic models
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class ImageRequest(BaseModel):
    image_data: str
    filename: str = "image.jpg"
    content_type: str = "image/jpeg"

class AnalysisResponse(BaseModel):
    id: int
    filename: str
    classification: str
    confidence: float
    cancer_probability: float
    prediction: str
    is_positive: bool
    processing_time: float
    created_at: str

# ML Model setup
device = torch.device("cpu")
MODEL_PATH = "D:/New folder 1/efficientnet_esophagus_best.pth"

model = models.efficientnet_b0(weights=None)
num_ftrs = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_ftrs, 8)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

class_names = ["class0","class1","class2","class3","class4","class5","class6","class7"]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],[0.229, 0.224, 0.225])
])

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    conn = sqlite3.connect('esophascan.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, expires_at FROM sessions WHERE token = ?
    ''', (token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id, expires_at = result
    if datetime.fromisoformat(expires_at) < datetime.now():
        raise HTTPException(status_code=401, detail="Token expired")
    
    return user_id

# Authentication endpoints
@app.post("/auth/register")
async def register(user: UserRegister):
    try:
        conn = sqlite3.connect('esophascan.db')
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (user.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        password_hash = hash_password(user.password)
        cursor.execute('''
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        ''', (user.name, user.email, password_hash))
        
        conn.commit()
        conn.close()
        
        return {"message": "Registration successful", "status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
async def login(credentials: UserLogin):
    try:
        conn = sqlite3.connect('esophascan.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, password_hash FROM users WHERE email = ?
        ''', (credentials.email,))
        
        result = cursor.fetchone()
        
        if not result or not verify_password(credentials.password, result[2]):
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id, user_name, _ = result
        
        # Generate token
        token = generate_token()
        expires_in = timedelta(days=30 if credentials.remember_me else 1)
        expires_at = datetime.now() + expires_in
        
        cursor.execute('''
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (token, user_id, expires_at.isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_name": user_name,
            "expires_in": int(expires_in.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/verify")
async def verify_token(user_id: int = Depends(get_current_user)):
    return {"status": "valid", "user_id": user_id}

@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    conn = sqlite3.connect('esophascan.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()
    return {"message": "Logged out successfully"}

# Analysis endpoints
@app.post("/predict")
async def predict_with_save(request: ImageRequest, user_id: int = Depends(get_current_user)):
    try:
        start_time = datetime.now()
        
        # Decode and process image
        image_bytes = base64.b64decode(request.image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_t = transform(image).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            outputs = model(img_t)
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            conf, pred = torch.max(probs, 0)
            
        classification = class_names[pred.item()]
        confidence = float(conf.item())
        cancer_probability = float(probs[pred.item()].item())
        is_positive = bool(cancer_probability > 0.5) 
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        conn = sqlite3.connect('esophascan.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (user_id, filename, classification, confidence, cancer_probability, prediction, is_positive, processing_time, image_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            request.filename,
            classification,
            confidence,
            cancer_probability,
            classification,
            is_positive,
            processing_time,
            request.image_data
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return AnalysisResponse(
            id=analysis_id,
            filename=request.filename,
            classification=classification,
            confidence=confidence,
            cancer_probability=cancer_probability,
            prediction=classification,
            is_positive=is_positive,
            processing_time=processing_time,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))