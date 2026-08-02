# Architecture

This document explains how data flows through the system and why key design decisions were made.

## High-Level Flow

```
┌─────────────┐      HTTP POST      ┌──────────────┐      Python call     ┌────────────────┐
│  Frontend    │  (multipart/form)   │  FastAPI      │  ───────────────►   │  DeblurGAN-v2    │
│  (browser)   │ ──────────────────► │  Backend      │                      │  (PyTorch model)  │
│              │                     │              │  ◄───────────────   │                    │
│              │  ◄──────────────── │              │     numpy array      │                    │
└─────────────┘   JSON + image URL   └──────────────┘                      └────────────────┘
```

1. User selects/drops an image in the browser (`frontend/script.js`)
2. Browser sends it as `multipart/form-data` to `POST /deblur`
3. FastAPI (`backend/app.py`) receives the raw bytes
4. `preprocess.py` decodes bytes → OpenCV BGR numpy array
5. `inference.py` runs the array through the loaded DeblurGAN-v2 model
6. `postprocess.py` encodes the result numpy array back into PNG bytes
7. The result is saved to `outputs/`, and the API returns a JSON response with a download URL
8. The frontend fetches that URL and displays the restored image

## Why the model loads once, not per-request

Loading DeblurGAN-v2's weights involves reading a ~13 MB file from disk and initializing PyTorch's CUDA context — this takes a few seconds. If we loaded the model inside the `/deblur` route itself, **every single request would pay that cost**, making the app unusably slow.

Instead, `app.py` uses FastAPI's `lifespan` context manager to call `get_engine()` exactly once, when the server process starts. `inference.py` also guards this with a module-level singleton (`_engine`), so even if `get_engine()` is called from multiple places, the model is only ever loaded a single time in memory.

## Why we reused DeblurGAN-v2's own `Predictor` class instead of reimplementing it

The original repository's preprocessing (image padding to multiples of 32, specific normalization values matching how the model was trained) is precise and easy to get subtly wrong if reimplemented from scratch. Rather than risk introducing bugs that silently degrade output quality, `inference.py` directly imports and wraps the repo's `Predictor` class. This guarantees our results match what we already verified working in Phase 5 of development, before any web layer was added.

One consequence: `Predictor.__init__` opens `config/config.yaml` using a path relative to the `deblurganv2/` folder. Since our FastAPI server runs from the project root, `inference.py` temporarily changes the working directory only during model loading, then restores it — this keeps `deblurganv2`'s internal assumptions intact without affecting the rest of the app (e.g., where `uploads/` and `outputs/` are resolved).

## Why the pipeline is split into three backend files

- **`preprocess.py`** — only responsible for turning raw bytes into a format the model understands. Knows nothing about the model or FastAPI.
- **`inference.py`** — only responsible for the model itself: loading it and running it. Knows nothing about HTTP or file uploads.
- **`postprocess.py`** — only responsible for turning model output back into encoded image bytes. Knows nothing about the model internals or the web layer.

This separation (each module has one clear responsibility) means any piece can be tested, replaced, or debugged independently — for example, swapping in a different deblurring model later would only require changing `inference.py`, not touching the API or the byte-conversion logic.

## Why CORS is enabled with `allow_origins=["*"]`

The frontend is opened directly as a local file (`file:///...`) rather than served from the same origin as the backend (`http://127.0.0.1:8000`). Browsers block cross-origin requests by default, so without CORS middleware, the frontend's `fetch()` calls to the backend would fail. `allow_origins=["*"]` is appropriate here since this is a local development/academic project with no public deployment — it would need tightening (specific allowed origins) if this were ever deployed publicly.

## Why images are saved to disk instead of returned directly as response bytes

`POST /deblur` returns a small JSON payload (a filename and URL) rather than embedding the image bytes directly in that response. This keeps the API predictable and cacheable: the frontend can display the result via a normal `<img src="...">` tag pointing at `GET /download/{filename}`, and the same URL can be reused for the download button — no need to convert bytes to a data URL or handle binary responses differently on the frontend.

## Known Limitations

- The model was trained on the GoPro dataset (motion blur from camera/subject movement). It does not correct out-of-focus blur or artistic blur effects.
- `uploads/` and `outputs/` grow over time since files aren't automatically cleaned up — acceptable for a demo/academic project, but would need a cleanup job (e.g., delete files older than N hours) in a production setting.
- The app assumes a
