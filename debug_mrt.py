from database_manager import DatabaseManager
import pandas as pd

print("🚀 Starting MRT Debug...")
db = DatabaseManager()
db.load_data_lazily()

if db.mrt_df is not None:
    print("\n✅ MRT Data Loaded.")
    cols = list(db.mrt_df.columns)
    print(f"📊 Total Columns: {len(cols)}")
    
    # Print clean list
    clean_cols = [str(c).strip() for c in cols]
    print(f"DEBUG_COLS: {clean_cols[:30]}")
    
    # Test Search
    target = "桃園體育園區"
    print(f"\n🔍 Testing Search for: '{target}'")
    
    found = False
    for col in cols:
        c_str = str(col).replace(" ", "")
        # Logic check
        if target in c_str:
            print(f"   MATCH FOUND (Scenario 1): '{col}'")
            found = True
        if c_str in target and len(c_str) > 2:
             print(f"   MATCH FOUND (Scenario 2): '{col}'")
             found = True
             
    if not found:
        print("❌ No Direct Match Found.")
        
    # Print a sample of flow data for a known column if possible
    # e.g. "台北車站"
    # print(db.get_village_data('','','', '台北車站'))
    
else:
    print("❌ MRT Data Failed to Load.")
