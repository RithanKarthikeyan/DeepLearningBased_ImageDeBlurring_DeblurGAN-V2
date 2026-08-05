from pathlib import Path
import cv2
import sys
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.inference import get_engine

# Folders
BLUR_DIR = PROJECT_ROOT / "evaluation" / "blur"
SHARP_DIR = PROJECT_ROOT / "evaluation" / "sharp"
OUTPUT_DIR = PROJECT_ROOT / "evaluation" / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

engine = get_engine()

psnr_scores = []
ssim_scores = []

print("\nImage".ljust(30), "PSNR".ljust(12), "SSIM")
print("-" * 55)

for blur_path in BLUR_DIR.glob("*.*"):

    print(f"Processing {blur_path.name}...")

    image = cv2.imread(str(blur_path))
    result = engine.deblur(image)

    output_name = blur_path.stem + "_output.png"
    output_path = OUTPUT_DIR / output_name

    cv2.imwrite(str(output_path), cv2.cvtColor(result, cv2.COLOR_RGB2BGR))

# Ground truth image has the same filename
    sharp_path = SHARP_DIR / blur_path.name

    if not sharp_path.exists():
        print(f"Ground truth not found for {blur_path.name}")
        continue

    gt = cv2.imread(str(sharp_path))
    pred = cv2.imread(str(output_path))

    # Ensure same size
    pred = cv2.resize(pred, (gt.shape[1], gt.shape[0]))

    psnr = peak_signal_noise_ratio(gt, pred, data_range=255)

    ssim = structural_similarity(
        gt,
        pred,
        channel_axis=2,
        data_range=255
    )

    psnr_scores.append(psnr)
    ssim_scores.append(ssim)

    print(
        blur_path.name.ljust(30),
        f"{psnr:.2f}".ljust(12),
        f"{ssim:.4f}"
    )

print("-" * 55)
print(f"Average PSNR : {sum(psnr_scores)/len(psnr_scores):.2f} dB")
print(f"Average SSIM : {sum(ssim_scores)/len(ssim_scores):.4f}")