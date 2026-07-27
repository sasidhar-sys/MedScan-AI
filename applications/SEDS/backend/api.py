from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0
import io

# =========================
# 🚀 FASTAPI INIT
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 📁 MODEL PATH
# =========================
MODEL_PATH = "../model/model.pth"

# =========================
# 🧠 LOAD MODEL (MATCH TRAINING)
# =========================
model = efficientnet_b0(weights=None)

model.classifier = nn.Sequential(
    nn.Dropout(0.5),
    nn.Linear(model.classifier[1].in_features, 3)
)

model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# =========================
# 📊 CLASSES
# =========================
classes = ["Esophageal", "Lung_Cancer", "Normal"]

# =========================
# 🔄 TRANSFORM
# =========================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# =========================
# 🚀 API ROUTE
# =========================
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    img = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        probs = torch.softmax(outputs, dim=1)
        confidence, pred = torch.max(probs, 1)

    return {
        "prediction": classes[pred.item()],
        "confidence": round(confidence.item() * 100, 2)
    }