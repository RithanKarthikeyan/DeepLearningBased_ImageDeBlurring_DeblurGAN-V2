"""
app.py
-------
FastAPI server exposing a single endpoint that accepts a blurred image,
runs it through DeblurGAN-v2, and returns the restored result.

The model is loaded exactly once at server startup via FastAPI's
lifespan handler — not on every request, since loading is slow.
"""

import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

sys.path.insert(0, str(BACKEND_DIR))
from inference import get_engine
from postprocess import image_to_bytes
from preprocess import bytes_to_image

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Loading the model here means it happens once, when the server starts.
    get_engine()
    UPLOADS_DIR.mkdir(exist_ok=True)
    OUTPUTS_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(title="AI Image Deblurring API", lifespan=lifespan)

# Allows our frontend (served from a different origin, e.g. file:// or
# a different port) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/deblur")
async def deblur_image(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    raw_bytes = await file.read()

    try:
        image_bgr = bytes_to_image(raw_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    file_id = uuid.uuid4().hex
    upload_path = UPLOADS_DIR / f"{file_id}{extension}"
    upload_path.write_bytes(raw_bytes)

    engine = get_engine()
    result_rgb = engine.deblur(image_bgr)
    result_bytes = image_to_bytes(result_rgb, extension=".png")

    output_filename = f"{file_id}_deblurred.png"
    output_path = OUTPUTS_DIR / output_filename
    output_path.write_bytes(result_bytes)

    return {
        "result_filename": output_filename,
        "download_url": f"/download/{output_filename}",
    }


@app.get("/download/{filename}")
async def download_result(filename: str):
    file_path = OUTPUTS_DIR / filename

    if not file_path.exists() or file_path.parent != OUTPUTS_DIR:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="image/png", filename=filename)