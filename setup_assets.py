import os
import shutil

# 1. Setup Fonts
src_font_dir = "GenYoGothicTW"
dst_font_dir = "static/fonts"
os.makedirs(dst_font_dir, exist_ok=True)

font_files = [
    "GenYoGothicTW-Bold.ttf",
    "GenYoGothicTW-Medium.ttf",
    "GenYoGothicTW-Normal.ttf",
    "GenYoGothicTW-Light.ttf"
]

print("Moving fonts...")
for f in font_files:
    src = os.path.join(src_font_dir, f)
    dst = os.path.join(dst_font_dir, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied {f}")
    else:
        print(f"Missing {f}")

# 2. Rename Logo for easier access
# We suspect image_p0_0.jpeg is the logo/cover. Let's copy it to static/logo.png (or jpeg)
src_logo = "static/brand_assets/image_p0_0.jpeg"
dst_logo = "static/logo.jpeg"
if os.path.exists(src_logo):
    shutil.copy2(src_logo, dst_logo)
    print(f"Set Logo to {dst_logo}")
