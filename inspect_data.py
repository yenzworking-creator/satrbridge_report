import pandas as pd
import os

data_dir = os.path.join(os.getcwd(), 'data')
files_to_check = [
    "113年全台各村里性別人口統計.xlsx",
    "111年度綜稅所得應納稅額及稅率各縣市申報統計表 (2).xlsx",
    "202510各站進出量統計.xlsx",
    "全台租金 (1).xls"
]

for filename in files_to_check:
    path = os.path.join(data_dir, filename)
    if os.path.exists(path):
        print(f"\n=== File: {filename} ===")
        try:
            # Read first few rows
            if filename.endswith('xls'):
                 # engine='xlrd' might be needed for old xls, but openpyxl is default for xlsx
                 # pandas often handles xls with 'xlrd' dependency if installed, or we try default
                 df = pd.read_excel(path, nrows=3)
            else:
                 df = pd.read_excel(path, nrows=3)
            
            print(f"Columns: {df.columns.tolist()}")
            print("First row Sample:")
            print(df.iloc[0].to_dict())
        except Exception as e:
            print(f"Error reading: {e}")
    else:
        print(f"File not found: {filename}")
