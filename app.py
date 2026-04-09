import os
import time
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import cv2
from flask import Flask, jsonify, render_template, request
from ultralytics import YOLO  
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULT_DIR = BASE_DIR / "static" / "results"
MODEL_PATH = BASE_DIR / "best.pt"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
CONFIDENCE = 0.12
TTL_HOURS = 24
DISEASE_WORDS = ("disease", "blight", "spot", "mildew", "rust", "rot", "wilt", "mold", "fungal")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

model: Any = YOLO(str(MODEL_PATH))
names = cast(dict[int, str], model.names)
disease_ids = [idx for idx, name in names.items() if any(w in name.lower() for w in DISEASE_WORDS)]


def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup(folder: Path) -> None:
    cutoff = time.time() - TTL_HOURS * 3600
    for file in folder.glob("*"):
        if file.is_file() and file.stat().st_mtime < cutoff:
            try:
                file.unlink()
            except OSError:
                pass


def predict_image(path: Path, disease_only: bool) -> tuple[str, dict[str, Any]]:
    start = time.perf_counter()
    options: dict[str, Any] = {"source": str(path), "save": False, "verbose": False, "conf": CONFIDENCE, "iou": 0.45, "imgsz": 960}
    if disease_only and disease_ids:
        options["classes"] = disease_ids

    result = cast(list[Any], model.predict(**options))[0]
    raw: list[dict[str, Any]] = []

    boxes = result.boxes
    if boxes is not None:
        for cls_id, conf in zip(cast(list[float], boxes.cls.tolist()), cast(list[float], boxes.conf.tolist())):
            raw.append({"label": names[int(cls_id)], "confidence": round(float(conf) * 100, 2), "count": 1})

    merged: dict[str, dict[str, Any]] = {}
    for item in raw:
        label = str(item["label"])
        if label not in merged:
            merged[label] = item
        else:
            merged[label]["count"] = int(merged[label]["count"]) + 1
            merged[label]["confidence"] = max(float(merged[label]["confidence"]), float(item["confidence"]))

    detections = sorted(merged.values(), key=lambda x: float(x["confidence"]), reverse=True)
    top = detections[0] if detections else None
    message = "Disease pattern detected successfully." if detections else "No disease pattern detected in this image." if disease_only else "No objects detected with the current settings."

    image_name = f"result_{uuid4().hex}.jpg"
    cv2.imwrite(str(RESULT_DIR / image_name), result.plot())

    return image_name, {
        "total": len(detections),
        "raw_total": len(raw),
        "detections": detections,
        "mode": "disease-only" if disease_only and disease_ids else "all-classes",
        "latency_ms": round((time.perf_counter() - start) * 1000, 1),
        "top_detection": top,
        "message": message,
    }


@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok", "model_loaded": MODEL_PATH.exists()})


@app.route("/", methods=["GET", "POST"])
def index() -> Any:
    context: dict[str, Any] = {"image_name": None, "error": None, "result": None, "disease_only": True}

    if request.method == "POST":
        cleanup(UPLOAD_DIR)
        cleanup(RESULT_DIR)

        file = request.files.get("image")
        disease_only = request.form.get("disease_only") == "on"
        context["disease_only"] = disease_only

        if not file or not file.filename:
            context["error"] = "Please select an image file first."
            return render_template("index.html", **context)

        if not allowed_file(file.filename):
            context["error"] = "Unsupported file type. Use JPG, JPEG, PNG, or WEBP."
            return render_template("index.html", **context)

        ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
        upload_name = f"upload_{uuid4().hex}.{ext}"
        upload_path = UPLOAD_DIR / upload_name
        file.save(upload_path)

        try:
            image_name, result = predict_image(upload_path, disease_only)
            context["image_name"] = f"results/{image_name}"
            context["result"] = result
        except Exception:
            context["error"] = "Prediction failed. Please try another image."

        return render_template("index.html", **context)

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=os.getenv("FLASK_DEBUG") == "1", use_reloader=False)
