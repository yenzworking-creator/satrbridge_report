from PIL import Image
from collections import Counter
import os

def get_dominant_color(image_path, k=2):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((150, 150)) # Resize for speed
        
        # Simple frequency
        pixels = list(img.getdata())
        counts = Counter(pixels)
        
        # Get most common
        # Filter out white/near-white and black/near-black if possible to find "Brand Color"
        filtered_counts = {}
        for rgb, count in counts.items():
            r, g, b = rgb
            # Ignore white-ish
            if r > 240 and g > 240 and b > 240: continue
            # Ignore black-ish
            if r < 15 and g < 15 and b < 15: continue
            filtered_counts[rgb] = count
            
        if not filtered_counts:
            return "#0f172a" # Fallback Dark Slate
            
        # Sort
        most_common = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
        top_rgb = most_common[0][0]
        
        return '#{:02x}{:02x}{:02x}'.format(top_rgb[0], top_rgb[1], top_rgb[2])

    except Exception as e:
        print(f"Error: {e}")
        return "#6366f1" # Fallback Indigo

# Analyze all images in brand_assets
assets_dir = "static/brand_assets"
if os.path.exists(assets_dir):
    for filename in os.listdir(assets_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(assets_dir, filename)
            color = get_dominant_color(full_path)
            print(f"File: {filename} -> Dominant Color: {color}")
else:
    print("Assets directory not found")
