import io
import base64
import torch
import torch.nn as nn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from torchvision import models, transforms
from PIL import Image
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt

app = FastAPI(title="EsophaScan AI", description="Medical Imaging Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "your-secret-key-change-in-production-use-long-random-string"
ALGORITHM = "HS256"


users_db = {}


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



def verify_token(authorization: Optional[str] = Header(None)):
    """Verify JWT token and return user email"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        
        if email is None or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/auth/register")
async def register(user: UserRegister):
    """Register a new user"""
    try:
        if user.email in users_db:
            return JSONResponse(
                content={"detail": "Email already registered"},
                status_code=400
            )
        
        if len(user.password) < 8:
            return JSONResponse(
                content={"detail": "Password must be at least 8 characters long"},
                status_code=400
            )
        

        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'),
            bcrypt.gensalt()
        )
        
        users_db[user.email] = {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "created_at": datetime.now().isoformat(),
            "analyses": [] 
        }
        
        return {
            "message": "User registered successfully",
            "email": user.email,
            "name": user.name
        }
        
    except Exception as e:
        return JSONResponse(
            content={"detail": f"Registration failed: {str(e)}"},
            status_code=500
        )

@app.post("/auth/login")
async def login(credentials: UserLogin):
    """Login user and return JWT token"""
    try:
        user = users_db.get(credentials.email)
        
        if not user:
            return JSONResponse(
                content={"detail": "Invalid email or password"},
                status_code=401
            )
        
        if not bcrypt.checkpw(
            credentials.password.encode('utf-8'),
            user["password"]
        ):
            return JSONResponse(
                content={"detail": "Invalid email or password"},
                status_code=401
            )
        
        expiry = timedelta(days=30 if credentials.remember_me else 1)
        token_data = {
            "email": credentials.email,
            "exp": datetime.utcnow() + expiry
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "token": token,
            "email": credentials.email,
            "name": user["name"],
            "message": "Login successful"
        }
        
    except Exception as e:
        return JSONResponse(
            content={"detail": f"Login failed: {str(e)}"},
            status_code=500
        )

@app.get("/auth/profile")
async def get_profile(user_email: str = Depends(verify_token)):
    """Get user profile (requires authentication)"""
    user = users_db.get(user_email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
        "total_analyses": len(user["analyses"])
    }

@app.get("/auth/history")
async def get_analysis_history(user_email: str = Depends(verify_token)):
    """Get user's analysis history (requires authentication)"""
    user = users_db.get(user_email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "email": user_email,
        "analyses": user["analyses"]
    }


@app.get("/")
async def root():
    return {
        "message": "EsophaScan AI - Medical Imaging Analysis API",
        "status": "active",
        "endpoints": {
            "authentication": ["/auth/register", "/auth/login", "/auth/profile"],
            "prediction": ["/predict", "/predict-file"],
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": True,
        "users_registered": len(users_db)
    }

@app.post("/predict")
async def predict_base64(
    request: ImageRequest,
    authorization: Optional[str] = Header(None)
):
    """Predict cancer from base64 image (optional authentication)"""
    try:
       
        user_email = None
        if authorization:
            try:
                user_email = verify_token(authorization)
            except:
                pass  
    
        image_bytes = base64.b64decode(request.image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
      
        img_t = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(img_t)
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            conf, pred = torch.max(probs, 0)
        
        result = {
            "cancer_probability": round(float(probs[pred]) * 100, 2),
            "confidence": round(float(conf) * 100, 2),
            "indicators": class_names[pred],
            "filename": request.filename,
            "model_version": "EfficientNet-B0 v1.0",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }

        if user_email and user_email in users_db:
            users_db[user_email]["analyses"].append({
                "timestamp": datetime.now().isoformat(),
                "filename": request.filename,
                "result": result
            })
            result["saved_to_history"] = True
        
        return JSONResponse(content=result)
        
    except Exception as e:
        error_response = {
            "error": str(e),
            "status": "error",
            "message": "Failed to process image"
        }
        return JSONResponse(content=error_response, status_code=500)

from fastapi import UploadFile, File

@app.post("/predict-file")
async def predict_file(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Predict cancer from uploaded file (optional authentication)"""
    try:
        user_email = None
        if authorization:
            try:
                user_email = verify_token(authorization)
            except:
                pass
        
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_t = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(img_t)
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            conf, pred = torch.max(probs, 0)
        
        result = {
            "cancer_probability": round(float(probs[pred]) * 100, 2),
            "confidence": round(float(conf) * 100, 2),
            "indicators": class_names[pred],
            "filename": file.filename,
            "model_version": "EfficientNet-B0 v1.0",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
        if user_email and user_email in users_db:
            users_db[user_email]["analyses"].append({
                "timestamp": datetime.now().isoformat(),
                "filename": file.filename,
                "result": result
            })
            result["saved_to_history"] = True
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "status": "error"},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    print("Starting EsophaScan AI Server...")
    print("Authentication endpoints available at /auth/register and /auth/login")
    uvicorn.run(app, host="127.0.0.1", port=8000)