import argparse
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b0
from PIL import Image

MODEL_PATH = "efficientnet_esophagus_best.pth"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = efficientnet_b0(weights=None)
model.classifier[1] = nn.Linear(1280, 8) 
state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict, strict=True)
model.to(device)
model.eval()

CLASSES = [
    "Class1",
    "Class2",
    "Class3",
    "Class4",
    "Class5",
    "Class6",
    "Class7",
    "Class8"
]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def predict(image_path):
    img = Image.open(image_path).convert("RGB")
    img_t = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(img_t)
        probs = torch.softmax(outputs, dim=1)
        conf, pred = torch.max(probs, 1)
    return CLASSES[pred.item()], conf.item() * 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to input image")
    args = parser.parse_args()

    label, confidence = predict(args.input)
    print(f"Prediction: {label} ({confidence:.2f}%)")