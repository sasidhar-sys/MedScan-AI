import torch
import torchvision.models as models
import torch.nn as nn
import os

CLASSES = ["Esophageal", "Lung_Cancer", "Normal"]

def load_model():
    # Attempt to load EfficientNet-B0
    model = models.efficientnet_b0(pretrained=False)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, 3)
    
    # Locate model.pth which is in the parent's model directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    weights_path = os.path.join(os.path.dirname(current_dir), "model", "model.pth")
    
    if os.path.exists(weights_path):
        try:
            model.load_state_dict(torch.load(weights_path, map_location='cpu'))
            print("Loaded fine-tuned model weights successfully from", weights_path)
        except Exception as e:
            print(f"Failed to load weights: {e}. Using un-trained model.")
    else:
        print(f"Weights file not found at {weights_path}. Using base model.")
        
    model.eval()
    return model

def predict_image(model, image_tensor):
    with torch.no_grad():
        output = model(image_tensor)
        prob = torch.softmax(output, dim=1)
        confidence, pred_idx = torch.max(prob, 1)
        
    pred_class = CLASSES[pred_idx.item()]
    prob_val = confidence.item() * 100.0
    
    # Calculate Risk Level and Message
    if pred_class in ["Esophageal", "Lung_Cancer"]:
        risk = "HIGH RISK" if prob_val >= 80 else "MEDIUM RISK"
        message = "Consult an oncologist immediately." if risk == "HIGH RISK" else "Further medical evaluation recommended."
    else:
        risk = "CLEAR" if prob_val >= 60 else "MEDIUM RISK"
        if risk == "MEDIUM RISK":
             message = "Normal prediction with low confidence. Consider a follow-up."
        else:
             risk = "CLEAR"
             message = "No significant abnormalities detected. Routine checkup advised."

    return pred_class, prob_val, risk, message