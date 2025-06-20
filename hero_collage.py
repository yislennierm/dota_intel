import os
import cv2
import math
import numpy as np
import random

# Paths
SOURCE_FOLDER = "hero_full"
OUTPUT_FOLDER = "hero_collages"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Collage configuration
images_per_row = 10
rows_per_collage = 6
images_per_collage = images_per_row * rows_per_collage
image_size = (128, 72)  # Width, Height

# Load and shuffle hero images
image_files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
random.shuffle(image_files)

# Split into chunks for multiple collages
chunks = [image_files[i:i + images_per_collage] for i in range(0, len(image_files), images_per_collage)]

for index, chunk in enumerate(chunks):
    collage_height = rows_per_collage * image_size[1]
    collage_width = images_per_row * image_size[0]
    collage = np.zeros((collage_height, collage_width, 3), dtype=np.uint8)

    for idx, filename in enumerate(chunk):
        img_path = os.path.join(SOURCE_FOLDER, filename)
        img = cv2.imread(img_path)
        if img is None:
            continue
        img_resized = cv2.resize(img, image_size)

        row = idx // images_per_row
        col = idx % images_per_row
        y1 = row * image_size[1]
        y2 = y1 + image_size[1]
        x1 = col * image_size[0]
        x2 = x1 + image_size[0]
        collage[y1:y2, x1:x2] = img_resized

    collage_filename = f"hero_collage_{index+1:03}.png"
    collage_path = os.path.join(OUTPUT_FOLDER, collage_filename)
    cv2.imwrite(collage_path, collage)
    print(f"✅ Saved: {collage_path}")
