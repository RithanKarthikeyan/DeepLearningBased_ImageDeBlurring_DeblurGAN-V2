import numpy as np
import cv2

def bytes_to_image(file_bytes: bytes) -> np.ndarray:

    file_array = np.frombuffer(file_bytes, dtype=np.uint8)
    image_bgr = cv2.imdecode(file_array, cv2.IMREAD_COLOR)

    if image_bgr is None:
        raise ValueError("Uploaded file is not a valid image")

    return image_bgr