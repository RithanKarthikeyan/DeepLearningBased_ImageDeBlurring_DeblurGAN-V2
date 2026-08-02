# AI-Powered Blind Image Deblurring System

A full-stack web application that restores motion-blurred images using **DeblurGAN-v2**, running entirely on your local machine — no cloud APIs, no external services.

## Overview

Upload a blurred photo through the browser, and the app runs it through a pretrained DeblurGAN-v2 model (PyTorch) via a local FastAPI backend, then displays the restored result alongside the original for comparison and download.

## Tech Stack

| Layer | Technology |
|---|---|
| Deep Learning | PyTorch, DeblurGAN-v2 (FPN + MobileNet backbone) |
| Backend API | FastAPI, Uvicorn |
| Frontend | HTML, CSS, vanilla JavaScript |
| Image Processing | OpenCV, Pillow |

## Project Structure

```
AI-Image-Deblurring/
├── backend/
│   ├── app.py            # FastAPI server & API routes
│   ├── inference.py       # Loads the model once, runs deblurring
│   ├── preprocess.py      # Converts uploaded bytes → model input
│   └── postprocess.py     # Converts model output → response bytes
├── deblurganv2/            # Official DeblurGAN-v2 repository (model code)
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── weights/                 # Pretrained model weights (.h5)
├── uploads/                 # Temporary storage for uploaded images
├── outputs/                 # Generated deblurred results
└── requirements.txt
```

## Setup Instructions

### 1. Clone and create a virtual environment

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
```

> Python 3.11 is required — DeblurGAN-v2's dependencies are not compatible with newer Python versions.

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

> If installing PyTorch with GPU (CUDA) support, install it separately first:
> ```powershell
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
> ```

### 3. Download pretrained weights

Download `fpn_mobilenet.h5` from the [DeblurGAN-v2 releases](https://github.com/VITA-Group/DeblurGANv2) and place it in `weights/`.

### 4. Run the backend server

```powershell
uvicorn backend.app:app --reload
```

The API will be live at `http://127.0.0.1:8000`. Interactive docs: `http://127.0.0.1:8000/docs`.

### 5. Open the frontend

Open `frontend/index.html` directly in your browser (double-click it, or use a Live Server extension).

## How It Works

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for a full breakdown of the request/response flow and design decisions.

## Model Credit

This project uses the pretrained **DeblurGAN-v2** model by Kupyn, Martyniuk, Wu, and Wang (ICCV 2019). Original repository: [VITA-Group/DeblurGANv2](https://github.com/VITA-Group/DeblurGANv2).

## Limitations

- Optimized for **motion blur** (camera shake, fast-moving subjects) — not out-of-focus or artistic blur.
- Runs on CPU if no CUDA-capable GPU is available (slower per image).