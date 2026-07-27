"""
╔══════════════════════════════════════════════════════════════════╗
║  POCKETSCAN AI — Flask Backend API                               ║
║  Loads real EfficientNet-B0 model → serves accurate predictions  ║
║                                                                  ║
║  HOW TO RUN:                                                     ║
║    pip install flask flask-cors torch torchvision pillow         ║
║    python app.py                                                 ║
║                                                                  ║
║  Then open frontend at:  http://127.0.0.1:5502/frontend/         ║
║  API runs at:            http://127.0.0.1:5000                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import io
import os
import sys
import base64
import logging
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models, transforms
from torchvision.models import EfficientNet_B0_Weights
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("PocketScanAPI")

# ── App ───────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow frontend to call this API from any origin

# ── Config ────────────────────────────────────────────────────────
MODEL_PATH   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "model.pth")
DEVICE       = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES  = ["Esophageal", "Lung_Cancer", "Normal"]
IMG_SIZE     = 224
MAX_IMG_BYTES = 20 * 1024 * 1024  # 20 MB

# Minimum confidence threshold — if max confidence < this, reject as wrong scan type
CONFIDENCE_THRESHOLD = 0.50

# ── Model globals ─────────────────────────────────────────────────
model        = None
class_names  = None

# ── Preprocessing ─────────────────────────────────────────────────
TRANSFORM = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225],
    ),
])


# ══════════════════════════════════════════════════════════════════
#  BUILD MODEL — same architecture as train.py
# ══════════════════════════════════════════════════════════════════
def build_model(num_classes: int, dropout_rate: float = 0.4) -> nn.Module:
    m = models.efficientnet_b0(weights=None)
    in_features = m.classifier[1].in_features
    m.classifier = nn.Sequential(
        nn.Dropout(p=dropout_rate, inplace=True),
        nn.Linear(in_features, 512),
        nn.SiLU(),
        nn.Dropout(p=dropout_rate * 0.5),
        nn.Linear(512, num_classes),
    )
    return m


# ══════════════════════════════════════════════════════════════════
#  LOAD MODEL
# ══════════════════════════════════════════════════════════════════
def load_model():
    global model, class_names

    if not Path(MODEL_PATH).exists():
        log.error(f"❌ Model file not found: {MODEL_PATH}")
        log.error("   Train the model first with: python train.py")
        log.error("   Then copy best_model.pth to this directory")
        model = None
        class_names = CLASS_NAMES
        return False

    try:
        checkpoint   = torch.load(MODEL_PATH, map_location=DEVICE)
        
        # Check if it's a wrapper dict or just a raw state_dict
        if "model_state_dict" in checkpoint:
            class_names  = checkpoint.get("class_names", CLASS_NAMES)
            num_classes  = checkpoint.get("num_classes", len(class_names))
            dropout_rate = checkpoint.get("config", {}).get("dropout_rate", 0.4)
            model_state = checkpoint["model_state_dict"]
            val_acc = checkpoint.get("val_acc", 0)
            epoch   = checkpoint.get("epoch", "?")
        else:
            class_names = CLASS_NAMES
            num_classes = len(class_names)
            dropout_rate = 0.4
            model_state = checkpoint
            val_acc = 0
            epoch = "?"

        # Ensure correct classifier block structure (since backend uses a Sequential block, while train.py just sets Linear to 3)
        # Revert app.py to use standard EfficientNet-B0 classifier matching train.py
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        
        model.load_state_dict(model_state)
        model.to(DEVICE)
        model.eval()

        log.info(f"✅ Model loaded: {MODEL_PATH}")
        log.info(f"   Classes: {class_names}")
        log.info(f"   Best val accuracy: {val_acc*100:.2f}%  (epoch {epoch})")
        log.info(f"   Device: {DEVICE}")
        return True

    except Exception as e:
        log.error(f"❌ Failed to load model: {e}")
        model = None
        return False


# ══════════════════════════════════════════════════════════════════
#  PREDICT — runs real inference
# ══════════════════════════════════════════════════════════════════
def predict_image_bytes(img_bytes: bytes) -> dict:
    """
    Run the real EfficientNet-B0 model on image bytes.
    Returns a dict with class, confidence, and all scores.
    """
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    tensor = TRANSFORM(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.softmax(logits, dim=1).squeeze().cpu().numpy()

    pred_idx    = int(probs.argmax())
    pred_class  = class_names[pred_idx]
    confidence  = float(probs[pred_idx])
    all_scores  = {
        name: round(float(probs[i]) * 100, 2)
        for i, name in enumerate(class_names)
    }

    # If max confidence is below threshold, flag as uncertain / wrong scan type
    is_valid = confidence >= CONFIDENCE_THRESHOLD

    return {
        "class":       pred_class,
        "confidence":  round(confidence * 100, 2),
        "scores":      all_scores,
        "is_valid":    is_valid,
        "low_confidence": not is_valid,
    }


# ══════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════

@app.route("/health", methods=["GET"])
def health():
    """Health check — frontend polls this to verify the API is running."""
    return jsonify({
        "status":       "ok",
        "model_loaded": model is not None,
        "device":       str(DEVICE),
        "classes":      class_names or CLASS_NAMES,
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint.
    Accepts: multipart/form-data with field 'image' (image file or PDF)
    OR:      JSON with field 'image_b64' (base64-encoded image)
    Returns: JSON with prediction result.
    """
    if model is None:
        return jsonify({
            "error": "Model not loaded. Run: python train.py first, then restart the API.",
            "model_missing": True,
        }), 503

    # ── Get image bytes ──────────────────────────────────────────
    img_bytes = None

    if "image" in request.files or "file" in request.files:
        f = request.files.get("image") or request.files.get("file")
        img_bytes = f.read()
        log.info(f"Received file: {f.filename}  ({len(img_bytes)} bytes)")

    elif request.is_json and "image_b64" in request.json:
        b64 = request.json["image_b64"]
        # Strip data URL prefix if present
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        img_bytes = base64.b64decode(b64)
        log.info(f"Received base64 image ({len(img_bytes)} bytes)")

    if not img_bytes:
        return jsonify({"error": "No image provided. Send 'image' file or 'image_b64' base64."}), 400

    if len(img_bytes) > MAX_IMG_BYTES:
        return jsonify({"error": "Image too large. Max 20MB."}), 413

    # ── Run inference ────────────────────────────────────────────
    try:
        result = predict_image_bytes(img_bytes)
        log.info(f"Prediction: {result['class']}  ({result['confidence']:.1f}%)  "
                 f"valid={result['is_valid']}")
        return jsonify(result)

    except Exception as e:
        log.error(f"Prediction failed: {e}", exc_info=True)
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@app.route("/predict_pdf", methods=["POST"])
def predict_pdf():
    """
    Predict from a PDF file — extracts first page as image.
    Requires: pip install pdf2image poppler
    """
    if model is None:
        return jsonify({"error": "Model not loaded.", "model_missing": True}), 503

    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file provided."}), 400

    try:
        from pdf2image import convert_from_bytes
        pdf_bytes = request.files["pdf"].read()
        pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=200)
        if not pages:
            return jsonify({"error": "Could not extract image from PDF."}), 400

        buf = io.BytesIO()
        pages[0].save(buf, format="PNG")
        img_bytes = buf.getvalue()

        result = predict_image_bytes(img_bytes)
        result["source"] = "pdf_page_1"
        log.info(f"PDF prediction: {result['class']}  ({result['confidence']:.1f}%)")
        return jsonify(result)

    except ImportError:
        return jsonify({"error": "PDF support not installed. Run: pip install pdf2image"}), 501
    except Exception as e:
        log.error(f"PDF prediction failed: {e}", exc_info=True)
        return jsonify({"error": f"PDF prediction failed: {str(e)}"}), 500


# ══════════════════════════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  PocketScan AI — Backend API")
    log.info("=" * 60)

    ok = load_model()

    if not ok:
        log.warning("⚠️  Starting without model — /predict will return 503")
        log.warning("    Train first: python train.py")
        log.warning("    Then restart: python app.py")

    log.info(f"🚀 API starting on http://0.0.0.0:5000")
    log.info(f"   Health check: http://127.0.0.1:5000/health")
    log.info(f"   Predict:      http://127.0.0.1:5000/predict")
    log.info("=" * 60)

    app.run(host="0.0.0.0", port=5000, debug=False)