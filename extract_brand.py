import fitz  # PyMuPDF
import re
import os

pdf_path = "星橋創媒_品牌識別_1140326_ol.pdf"
output_dir = "static/brand_assets"
os.makedirs(output_dir, exist_ok=True)

def extract_brand_assets():
    print(f"Analyzing {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        print("PDF not found!")
        return

    doc = fitz.open(pdf_path)
    text_content = ""
    
    # 1. Image Extraction (Logo)
    print("Extracting images...")
    for i, page in enumerate(doc):
        text_content += page.get_text()
        
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            img_filename = f"image_p{i}_{img_index}.{ext}"
            img_path = os.path.join(output_dir, img_filename)
            with open(img_path, "wb") as f:
                f.write(image_bytes)
            print(f"Saved: {img_path}")

    # 2. Color Extraction (Hex Codes)
    print("\nExtracting Colors...")
    # Regex for Hex codes
    hex_colors = set(re.findall(r'#[0-9A-Fa-f]{6}', text_content))
    # Regex for CMYK or RGB content might be implicit text like "C:100 M:0..."
    # Let's just print surrounding text of "C:" or "R:"
    
    print("Found Hex Candidates:", hex_colors)
    
    # Print some text to see if we can find color names
    print("\nText Sample (First 500 chars):")
    print(text_content[:500])

if __name__ == "__main__":
    extract_brand_assets()
