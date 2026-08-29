#!/usr/bin/env python3
"""Prep a photo for ASCII conversion: remove background, boost contrast on the
subject only, composite on pure white so the background stays truly blank.

Usage: python prep_photo.py source-photo.jpg
Writes: source-prepped.png
"""
import sys
from pathlib import Path

import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    input_path = Path(input_path)
    img = Image.open(input_path).convert("RGBA")

    # 1. Remove background -> RGBA with a real alpha mask for the subject
    print("Removing background...")
    no_bg = remove(img)
    rgba = np.array(no_bg)
    alpha = rgba[:, :, 3]

    # 2. Boost local contrast with CLAHE, but only look at it through the mask
    #    so background noise never gets amplified.
    print("Boosting contrast (CLAHE) on subject only...")
    gray = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    # 3. Anywhere the subject mask is weak, force pure white (255) instead of
    #    whatever noisy pixel was there -- this is what makes the background
    #    collapse cleanly to blank space in the ASCII ramp.
    mask = alpha > 20  # subject pixels
    out_arr = np.full_like(contrasted, 255)
    out_arr[mask] = contrasted[mask]

    out = Image.fromarray(out_arr)
    out.save(output_path)
    print(f"Saved {output_path} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep_photo(sys.argv[1])
