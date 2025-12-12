from PIL import Image
from collections import Counter
import os

def get_palette(image_path, k=3):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((150, 150))
        
        pixels = list(img.getdata())
        # Filter mostly white/black
        filtered = [
            p for p in pixels 
            if not (p[0]>230 and p[1]>230 and p[2]>230) # Too white
            and not (p[0]<25 and p[1]<25 and p[2]<25)   # Too black
        ]
        
        if not filtered:
            return ["#000000"]

        counts = Counter(filtered)
        common = counts.most_common(k)
        
        palette = []
        for rgb, _ in common:
            hex_col = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
            palette.append(hex_col)
            
        return palette

    except Exception as e:
        return [str(e)]

assets_dir = "static/brand_assets"
if os.path.exists(assets_dir):
    print("Top colors from assets:")
    for f in sorted(os.listdir(assets_dir)):
        if f.endswith(".jpeg") or f.endswith(".png"):
            path = os.path.join(assets_dir, f)
            print(f"{f}: {get_palette(path)}")
