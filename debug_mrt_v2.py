import pandas as pd
import os

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

data_dir = r"c:\Users\YenzW\Desktop\tidal-cassini\data"
file_path = os.path.join(data_dir, "202510各站進出量統計.xlsx")

if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path, header=None)
        
        print("\n--- Rows 0-5 ---")
        print(df.iloc[0:6])
        
        print("\n--- Searching for '體育園區' ---")
        found = False
        for r_idx, row in df.iterrows():
            for c_idx, val in enumerate(row):
                if isinstance(val, str) and "體育園區" in val:
                    print(f"FOUND at Row {r_idx}, Col {c_idx}: '{val}'")
                    found = True
        
        if not found:
            print("NOT FOUND '體育園區' in valid cells.")
            
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File missing")
