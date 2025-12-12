import pandas as pd
import os
import glob

data_dir = os.path.join(os.getcwd(), 'data')
rent_files = glob.glob(os.path.join(data_dir, "全台租金*.xls*"))

if rent_files:
    target = rent_files[0]
    print(f"Inspecting {target}...")
    try:
        df = pd.read_excel(target, nrows=5)
        print("Columns:", df.columns.tolist())
        print("First row:", df.iloc[0].to_dict())
        
        # Check for unique values in potential 'floor' columns if name is ambiguous
        # Usually: '樓層', '總樓層', '租金', '坪數'
    except Exception as e:
        print(e)
else:
    print("No rental files found.")
