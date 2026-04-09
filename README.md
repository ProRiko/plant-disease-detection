# Plant Disease Detection

A simple Flask web app that uses a trained YOLO model to detect plant diseases from uploaded images.

## Features

- Upload image and run detection from browser
- Disease-focused detection mode
- Annotated output image preview
- Detection summary with confidence and region count
- Auto cleanup of old uploads/results
- Health endpoint

## Tech Stack

- Python
- Flask
- Ultralytics YOLO
- OpenCV

## Project Structure

- app.py: Flask server and inference logic
- best.pt: Trained YOLO model weights
- templates/index.html: Main UI template
- static/css/style.css: UI styles
- static/js/app.js: Frontend interactions
- uploads/: Uploaded input images
- static/results/: Generated output images

## Requirements

- Python 3.10+
- Git (optional, for version control)

## Setup

### 1) Clone repository

```bash
git clone https://github.com/ProRiko/plant-disease-detection.git
cd plant-disease-detection
```

### 2) Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Project

```bash
python app.py
```

Open your browser:

- http://127.0.0.1:5000

## How to Use

1. Open the app in browser.
2. Upload a JPG, JPEG, PNG, or WEBP image.
3. Click Run Detection.
4. View annotated image and summary panel.

## Health Check

- http://127.0.0.1:5000/health

Expected response:

```json
{"status":"ok","model_loaded":true}
```

## Troubleshooting

### Port already in use

Stop existing process using port 5000, then run again.

### Model not found

Make sure best.pt exists in the project root.

### Unsupported file type

Use one of: .jpg, .jpeg, .png, .webp

### Permission issue activating venv on Windows

Run PowerShell as admin once and allow local scripts:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Notes

- The app stores generated results in static/results.
- Old files in uploads and static/results are cleaned automatically.
- This uses Flask development server; use Gunicorn or similar for production deployment.
