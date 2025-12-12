import pandas as pd
import os
import glob
import pickle
from config import DATA_DIR

class DatabaseManager:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.pop_df = None
        self.tax_df = None
        self.mrt_df = None
        self.rent_df = None
        self.is_loaded = False

    def load_data_lazily(self):
        """
        Loads data only when needed, or in background.
        Uses pickle cache to speed up subsequent reloads.
        Optimized for LOW MEMORY usage (Render Free Tier 512MB).
        """
        if self.is_loaded:
            return

        cache_file = os.path.join(self.data_dir, "db_cache_v2.pkl")
        
        # Try load from cache
        if os.path.exists(cache_file):
            print("⚡ 發現快取檔案 (v2)，正在快速載入資料庫...")
            try:
                # Use 'rb' and load
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.pop_df = data.get('pop')
                    self.tax_df = data.get('tax')
                    self.mrt_df = data.get('mrt')
                    self.rent_df = data.get('rent')
                self.is_loaded = True
                print(f"✅ 資料庫載入完成 (來自快取)")
                return
            except Exception as e:
                print(f"快取載入失敗，將重新讀取原始檔: {e}")

        print("📥 正在讀取原始 Excel 檔案 (記憶體優化模式)...")
        
        # 1. Population (Only need specific cols)
        try:
            pop_file = os.path.join(self.data_dir, "113年全台各村里性別人口統計.xlsx")
            if os.path.exists(pop_file):
                # Columns usually: 統計年, 區域別, 村里名稱, 總人口, 男, 女
                # Try to load only relevant ones. But headers might vary.
                # Safe approach: Load all but use 'dtype' to optimize
                self.pop_df = pd.read_excel(pop_file) 
                self.pop_df.columns = self.pop_df.columns.str.strip()
                # Determine relevant columns
                cols_to_keep = [c for c in self.pop_df.columns if c in ['區域別', '村里名稱', '女', '男']]
                self.pop_df = self.pop_df[cols_to_keep].dropna()
                print(f"📊 [Pop] Loaded. {len(self.pop_df)} rows.")
        except Exception as e: print(f"Pop Load Error: {e}")

        # 2. Tax (Only need Tax Payers & Median)
        try:
            tax_file = os.path.join(self.data_dir, "111年度綜稅所得應納稅額及稅率各縣市申報統計表 (2).xlsx")
            if os.path.exists(tax_file):
                self.tax_df = pd.read_excel(tax_file)
                self.tax_df.columns = self.tax_df.columns.str.strip()
                # Check known columns
                keep = ['縣市別', '村里', '納稅單位(戶)', '中位數']
                actual_keep = [c for c in keep if c in self.tax_df.columns]
                self.tax_df = self.tax_df[actual_keep].dropna()
                print(f"📊 [Tax] Loaded. {len(self.tax_df)} rows.")
        except Exception as e: print(f"Tax Load Error: {e}")

        # 3. MRT (Flow matrix)
        try:
            mrt_file = os.path.join(self.data_dir, "202510各站進出量統計.xlsx")
            if os.path.exists(mrt_file):
                # ... Existing Header Logic ...
                temp_df = pd.read_excel(mrt_file, header=None, nrows=10) # READ ONLY 10 ROWS FIRST
                header_row_idx = 0
                for i in range(10):
                    row_str = temp_df.iloc[i].astype(str).values
                    if any("A18" in s or "A19" in s or "日期" in s or "車站" in s for s in row_str):
                        header_row_idx = i
                        break
                
                self.mrt_df = pd.read_excel(mrt_file, header=header_row_idx)
                self.mrt_df.columns = self.mrt_df.columns.astype(str).str.strip()
                # MRT df is usually small (rows = days of month, cols = stations). Keep as is.
        except Exception as e: print(f"❌ MRT Load Error: {e}")
            
        # 4. Rent (HEAVY! Optimization Critical)
        rent_files = glob.glob(os.path.join(self.data_dir, "全台租金*.xls*"))
        rent_frames = []
        
        # Define Columns we absolutely need
        # '鄉鎮市區', '土地區段位置建物區段門牌', '移轉層次', '總額元', '單價元平方公尺', '建物總面積平方公尺'
        required_cols = ['鄉鎮市區', '土地區段位置建物區段門牌', '移轉層次', '總額元', '單價元平方公尺', '建物總面積平方公尺']
        
        for rf in rent_files:
            try:
                # Use Pandas usecols callable to handle slight name variations (e.g. '單價元平方公尺' vs '單價')
                # But generic 'usecols' logic is tricky if headers vary.
                # Strategy: Read headers first? Too many files. 
                # Strategy: Read File. Select columns immediately. Drop NaN. Append.
                
                df = pd.read_excel(rf) # Read full
                df.columns = df.columns.str.strip()
                
                # Filter Columns
                found_cols = [c for c in df.columns if c in required_cols]
                
                if '鄉鎮市區' in found_cols: # Basic check
                    df_mini = df[found_cols].copy()
                    
                    # Drop rows where Area is 0 to save space
                    if '建物總面積平方公尺' in df_mini.columns:
                        df_mini = df_mini[df_mini['建物總面積平方公尺'] > 0]
                        
                    rent_frames.append(df_mini)
                
                # Force Garbage Collection
                del df
            except: pass
        
        if rent_frames:
            self.rent_df = pd.concat(rent_frames, ignore_index=True)
            print(f"✅ [Rent] Loaded. {len(self.rent_df)} rows. (Mem Optimized)")
        else:
            print("⚠️ [Rent] No files loaded.")

        self.is_loaded = True
        
        # Save Optimized Cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'pop': self.pop_df,
                    'tax': self.tax_df,
                    'mrt': self.mrt_df,
                    'rent': self.rent_df
                }, f)
            print("💾 已建立優化版快取 db_cache_v2.pkl")
        except Exception as e:
            print(f"⚠️ 無法建立快取: {e}")


    def get_village_data(self, city, district, village, mrt_station_name=None):
        if not self.is_loaded: self.load_data_lazily()
        
        result = {
            "Population": 0, "Male_Pop": 0, "Female_Pop": 0,
            "Tax_Payers": 0, "Income_Median": 0,
            "MRT_Station": mrt_station_name, "MRT_Flow": 0,
            "Rent_1F_Avg": 0, "Rent_Upper_Avg": 0, "Rent_Advice": "" 
        }
        
        norm_city = city.replace('台', '臺') if city else ""

        # Logic same as before, just ensuring loaded
        if self.pop_df is not None:
            try:
                # 1. Normalize Inputs
                search_city = norm_city
                search_dist = district.strip()
                search_village = village.strip()
                
                print(f"🔍 [DB Debug] 搜尋目標: {search_city} | {search_dist} | {search_village}")

                # 2. Filter Population (Columns: ['區域別', '村里名稱', '女', '男', '總人口'])
                # '區域別' likely contains "City District" e.g. "臺北市松山區" or just "松山區" depending on source.
                # We will use string contain search on '區域別' for both City and District to be safe.
                
                df = self.pop_df.astype(str)
                
                # Loose Match Strategy:
                # Check if '區域別' contains "District" AND ("City" OR is implicit)
                # Usually '區域別' is uniquely identifying like '新北市板橋區'
                
                keywords = [search_dist]
                if len(search_city) > 2: keywords.append(search_city[-2:]) # "北市"
                
                # Custom mask builder
                loc_mask = df['區域別'].apply(lambda x: all(k in x for k in keywords))
                
                # Village Match
                village_mask = df['村里名稱'] == search_village
                
                q = df[loc_mask & village_mask]
                
                # Retry Fuzzy Village
                if q.empty and len(search_village) > 2:
                     short_village = search_village.replace("里", "").replace("村", "")
                     village_mask_fuzzy = df['村里名稱'].str.contains(short_village)
                     q = df[loc_mask & village_mask_fuzzy]

                if not q.empty:
                    row = q.iloc[0]
                    m = int(float(row.get('男', 0))) # Column is '男'
                    f = int(float(row.get('女', 0))) # Column is '女'
                    result['Population'] = m + f
                    result['Male_Pop'] = m
                    result['Female_Pop'] = f
                    print(f"✅ [DB Success] 找到人口數據: {result['Population']} 人")
                else:
                    print(f"⚠️ [DB Warning] 找不到人口數據 (搜尋: {search_city}{search_dist} - {search_village})")

            except Exception as e: 
                print(f"❌ [DB Error] Population lookup failed: {e}")

        if self.tax_df is not None:
            try:
                # Tax Columns: ['縣市別', '村里', '納稅單位(戶)', '綜合所得總額', '平均數', '中位數'...]
                df = self.tax_df.astype(str)
                
                search_city_short = norm_city.replace("台", "").replace("臺", "")
                
                # Filter
                if not search_village:
                    print("⚠️ [DB Debug] 村里名稱為空，跳過納稅查詢以避免誤判")
                else:
                    # Proceed with tax lookup only if village exists
                    city_mask = df['縣市別'].str.contains(search_city_short)
                    # Tax file often splits City/District or merges them? 
                    # If '行政區' column is MISSING (as seen in logs), then '縣市別' or '村里' might contain it?
                    # Actually logs showed: ['縣市別', '村里', '納稅單位(戶)'...] -> WHERE IS DISTRICT?
                    # Maybe '村里' contains "District Village"? Or '縣市別' contains "City District"?
                    # Let's try matching District in '縣市別' OR '村里' just to be safe.
                    # Actually standard MOF tax data usually has "縣市", "行政區", "村里". 
                    # If only "縣市別" corresponds to City? And maybe "行政區" is missing from print?
                    # Wait, User logs: ['縣市別', '村里', '納稅單位(戶)'...] -> It seems District column is named something else or missing!
                    # Ah, standard file often has "行政區別" or merged. 
                    # Let's assume '縣市別' might be '新北市板橋區' or we search district in '村里' (unlikely).
                    # Let's try searching District in '縣市別' first (common in some files).
                    
                    dist_mask = df['縣市別'].str.contains(search_dist) | df['村里'].str.contains(search_dist)
                    
                    village_mask = df['村里'] == search_village
                    
                    q = df[city_mask & dist_mask & village_mask]
                    
                    if q.empty:
                         short_village = search_village.replace("里", "").replace("村", "")
                         village_mask_fuzzy = df['村里'].str.contains(short_village)
                         q = df[city_mask & dist_mask & village_mask_fuzzy]

                    if not q.empty:
                        row = q.iloc[0]
                        result['Tax_Payers'] = int(float(row.get('納稅單位(戶)', 0)))
                        result['Income_Median'] = float(row.get('中位數', 0))
                        print(f"✅ [DB Success] 找到納稅戶數: {result['Tax_Payers']}")
                    else:
                        print(f"⚠️ [DB Warning] 找不到納稅數據")
            except Exception as e:
                print(f"❌ [DB Error] Tax lookup failed: {e}")

        if self.mrt_df is not None and mrt_station_name:
            # Clean: "捷運江子翠站" -> "江子翠"
            clean_station = mrt_station_name.replace("捷運", "").replace("站", "")
            
            # Search COLUMNS not Rows
            target_col = None
            
            # Normalize Columns for search
            cols = self.mrt_df.columns
            
            # 1. Exact Match on Clean
            if clean_station in cols:
                target_col = clean_station
            
            # 2. Try adding "站" (e.g. "台北車站")
            elif clean_station + "站" in cols:
                target_col = clean_station + "站"

            # 3. Robust Fuzzy Match
            import re
            def normalize_station_name(name):
                # Remove English letters, Numbers, Spaces, "站", "捷運"
                # Keep only Chinese characters mostly
                s = str(name)
                s = re.sub(r'[A-Za-z0-9\s]', '', s) # Remove Code A19
                s = s.replace("捷運", "").replace("站", "").replace("車站", "")
                return s

            target_clean = normalize_station_name(clean_station)
            
            for col in cols:
                col_clean = normalize_station_name(col)
                if not target_clean or not col_clean: continue
                
                # Check exact match of "core" name
                if target_clean == col_clean:
                    target_col = col
                    break
                # Check contains
                if target_clean in col_clean:
                     target_col = col
                     break
            
            if target_col:
                print(f"✅ [DB Success] 找到捷運站數據: {target_col} (原始搜尋: {clean_station})")
                # Sum the column, ignoring non-numeric (first row usually ok if skipped by header)
                try:
                    # Convert to numeric, coerce errors to NaN, then sum
                    result['MRT_Flow'] = int(pd.to_numeric(self.mrt_df[target_col], errors='coerce').sum())
                    print(f"   -> 流量: {result['MRT_Flow']}")
                except Exception as e:
                    print(f"⚠️ Calculation Error: {e}")
                    result['MRT_Flow'] = 0
            
            else:
                print(f"⚠️ [DB Warning] 找不到捷運站: {clean_station} (Normalized Target: {target_clean})")
                print(f"   -> First 5 Cols Normalized: {[normalize_station_name(c) for c in list(cols)[:5]]}")
            


        return result

    def get_rental_analysis(self, city, district, address_road):
        if not self.is_loaded: self.load_data_lazily()
        
        stats = {
            "1F_Count": 0, "1F_Min": 0, "1F_Max": 0, "1F_Avg": 0,
            "Upper_Count": 0, "Upper_Avg": 0,
            "Estimated_Range": "無數據",
            "Data_Source_Count": 0
        }
        
        if self.rent_df is None or self.rent_df.empty:
            return stats

        try:
            # Filter Logic (Simpified for brevity, assume Logic from previous step)
            # 1. District
            mask = (self.rent_df['鄉鎮市區'] == district)
            df_dist = self.rent_df[mask].copy()
            if df_dist.empty: return stats

            # 2. Price/Ping
            price_col = '總額元' if '總額元' in df_dist.columns else '單價元平方公尺'
            area_col = '建物總面積平方公尺'
            df_dist = df_dist[df_dist[area_col] > 0]
            df_dist['Price_Per_Ping'] = df_dist[price_col] / (df_dist[area_col] * 0.3025)

            # 3. Road
            addr_col = '土地區段位置建物區段門牌'
            if address_road:
                df_road = df_dist[df_dist[addr_col].astype(str).str.contains(address_road)].copy()
                final_df = df_road if len(df_road) >= 3 else df_dist
            else:
                final_df = df_dist

            stats['Data_Source_Count'] = len(final_df)
            
            # 4. Floor
            floor_col = '移轉層次'
            mask_1f = final_df[floor_col].astype(str).str.contains('一層|1層')
            df_1f = final_df[mask_1f]
            df_upper = final_df[~mask_1f]

            if not df_1f.empty:
                prices = df_1f['Price_Per_Ping']
                stats['1F_Count'] = len(df_1f)
                stats['1F_Avg'] = int(prices.mean())
            
            if not df_upper.empty:
                prices = df_upper['Price_Per_Ping']
                stats['Upper_Count'] = len(df_upper)
                stats['Upper_Avg'] = int(prices.mean())

            # 5. Advice
            if stats['1F_Count'] >= 3:
                low = int(df_1f['Price_Per_Ping'].quantile(0.25))
                high = int(df_1f['Price_Per_Ping'].quantile(0.75))
                stats['Estimated_Range'] = f"{low} ~ {high}"
            elif stats['Upper_Count'] > 0:
                est = int(stats['Upper_Avg'] * 1.6)
                stats['Estimated_Range'] = f"{int(est*0.9)} ~ {int(est*1.1)} (推估)"
        except Exception as e:
            print(f"Error in rent analysis: {e}")

        return stats
