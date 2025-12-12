import pandas as pd
import os

data_dir = r"c:\Users\YenzW\Desktop\tidal-cassini\data"
file_path = os.path.join(data_dir, "202510各站進出量統計.xlsx")

if os.path.exists(file_path):
    try:
        xl = pd.ExcelFile(file_path)
        print(f"Sheets: {xl.sheet_names}")
        
        for sheet in xl.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(file_path, sheet_name=sheet, header=None)
            print(df.head(3))
            
            # Search for A19 or 體育
            for r_idx, row in df.iterrows():
                for c_idx, val in enumerate(row):
                    s_val = str(val)
                    if "A19" in s_val or "體育" in s_val:
                         print(f"MATCH: '{s_val}' at ({r_idx}, {c_idx})")
    except Exception as e:
        print(f"Error: {e}")
