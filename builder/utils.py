from PIL import Image
import numpy as np

def load_img_rgba(path):
    return np.array(Image.open(path).convert("RGBA"))

def norm_to_px(nx, ny, W, H):
    # position is top-left anchoring for simplicity
    return int(nx*W), int(ny*H)