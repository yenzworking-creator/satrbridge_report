import fitz
import re

pdf_path = "星橋創媒_品牌識別_1140326_ol.pdf"

try:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    # improved regex for #RRGGBB
    # often in designs it might be "C:0 M:100..."
    # or "Color: #FF0000"
    hex_colors = set(re.findall(r'#[0-9A-Fa-f]{6}', text))
    print(f"Found {len(hex_colors)} Hex Codes:")
    print(list(hex_colors))
    
    # Check for CMYK patterns just in case
    cmyk = re.findall(r'[CMYKcmyk]\s*[:=]\s*\d+', text)
    if cmyk:
        print("Found CMYK candidates (sample):", cmyk[:10])

except Exception as e:
    print(e)
