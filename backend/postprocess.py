import numpy as np
import cv2


def image_to_bytes(image_rgb: np.ndarray, extension: str = ".png") -> bytes:
    """Encode an RGB numpy array into image file bytes (PNG by default)."""
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    success, encoded = cv2.imencode(extension, image_bgr)

    if not success:
        raise ValueError("Failed to encode image")

    return encoded.tobytes()