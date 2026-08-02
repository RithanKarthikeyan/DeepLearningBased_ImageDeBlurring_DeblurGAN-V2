

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import numpy as np


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DEBLURGAN_DIR = PROJECT_ROOT / "deblurganv2"
WEIGHTS_PATH = PROJECT_ROOT / "weights" / "fpn_mobilenet.h5"

sys.path.insert(0, str(DEBLURGAN_DIR))


@contextmanager
def _working_directory(path: Path):
    
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


class DeblurEngine:
    

    def __init__(self) -> None:
        with _working_directory(DEBLURGAN_DIR):
            from predict import Predictor  # imported after cwd is correct
            self._predictor = Predictor(weights_path=str(WEIGHTS_PATH.resolve()))

    def deblur(self, image_bgr: np.ndarray) -> np.ndarray:
        
        import cv2
        mask = np.ones_like(image_bgr, dtype="uint8")
        result_bgr = self._predictor(image_bgr, mask)
        return cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)


_engine: Optional[DeblurEngine] = None


def get_engine() -> DeblurEngine:
    global _engine
    if _engine is None:
        _engine = DeblurEngine()
    return _engine

