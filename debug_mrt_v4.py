import pandas as pd
import os

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

data_dir = r"c:\Users\YenzW\Desktop\tidal-cassini\data"
file_path = os.path.join(data_dir, "202510各站進出量統計.xlsx")

if os.path.exists(file_path):
    try:
        # Load first sheet
        df = pd.read_excel(file_path)
        print("--- Columns ---")
        print(df.columns.tolist())
        
        print("\n--- Head (5x5) ---")
        print(df.iloc[:5, :5])
        
        # Check first column unique values
        col0 = df.columns[0]
        print(f"\n--- First Column ({col0}) Unique Values (First 10) ---")
        print(df[col0].unique()[:10])
        
    except Exception as e:
        print(f"Error: {e}")
