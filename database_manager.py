import pandas as pd
import os
import glob
import pickle
from config import DATA_DIR
import sqlite3

DB_PATH = os.path.join(DATA_DIR, "starbridge.db")

class DatabaseManager:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.db_path = DB_PATH
        self.is_loaded = True # Always True as we query on demand

    def load_data_lazily(self):
        # No-op for SQLite version
        pass

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def get_village_data(self, city, district, village, mrt_station_name=None):
        result = {
            "Population": 0, "Male_Pop": 0, "Female_Pop": 0,
            "Tax_Payers": 0, "Income_Median": 0,
            "MRT_Station": mrt_station_name, "MRT_Flow": 0,
            "Rent_1F_Avg": 0, "Rent_Upper_Avg": 0, "Rent_Advice": "" 
        }
        
        conn = self._get_conn()
        try:
            # 1. Population (Table: population) - Cols: 區域別, 村里名稱, 男, 女
            # "區域別" like "新北市板橋區"
            # Logic: loose match
            
            # Simple Exact + Like search
            search_list = [f"%{district}%", village]
            
            # SQL Query
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 男, 女 FROM population 
                WHERE 區域別 LIKE ? AND 村里名稱 = ?
            """, search_list)
            row = cursor.fetchone()
            
            if not row and len(village) > 2: # Fuzzy Village
                 v_short = village.replace("里", "").replace("村", "")
                 cursor.execute("""
                    SELECT 男, 女 FROM population 
                    WHERE 區域別 LIKE ? AND 村里名稱 LIKE ?
                """, [f"%{district}%", f"%{v_short}%"])
                 row = cursor.fetchone()

            if row:
                m, f = row[0], row[1]
                result['Male_Pop'] = int(m)
                result['Female_Pop'] = int(f)
                result['Population'] = int(m + f)
                print(f"✅ [DB] Pop Found: {result['Population']}")
            
            # 2. Tax (Table: tax_stats) - Cols: 縣市別, 村里, 納稅單位(戶), 中位數
            # "縣市別" usually City+District or just City? Assume City+District often
            # We search "縣市別" LIKE district
            
            cursor.execute("""
                SELECT `納稅單位(戶)`, `中位數` FROM tax_stats 
                WHERE (`縣市別` LIKE ? OR `村里` LIKE ?) AND `村里` = ?
            """, [f"%{district}%", f"%{district}%", village])
            row = cursor.fetchone()
            
            if not row and len(village) > 2:
                 v_short = village.replace("里", "").replace("村", "")
                 cursor.execute("""
                    SELECT `納稅單位(戶)`, `中位數` FROM tax_stats 
                    WHERE (`縣市別` LIKE ? OR `村里` LIKE ?) AND `村里` LIKE ?
                """, [f"%{district}%", f"%{district}%", f"%{v_short}%"])
                 row = cursor.fetchone()
                 
            if row:
                result['Tax_Payers'] = int(row[0])
                result['Income_Median'] = float(row[1])
                print(f"✅ [DB] Tax Found: {result['Income_Median']}")

            # 3. MRT (Table: mrt_flow) - Cols: station_name, total_flow
            if mrt_station_name:
                clean_station = mrt_station_name.replace("捷運", "").replace("站", "")
                
                # Try Exact
                cursor.execute("SELECT total_flow FROM mrt_flow WHERE station_name = ?", [clean_station])
                row = cursor.fetchone()
                
                # Try LIKE
                if not row:
                    cursor.execute("SELECT total_flow FROM mrt_flow WHERE station_name LIKE ?", [f"%{clean_station}%"])
                    row = cursor.fetchone()
                
                if row:
                    result['MRT_Flow'] = int(row[0])
                    print(f"✅ [DB] MRT Found: {result['MRT_Flow']}")

        except Exception as e:
            print(f"❌ DB Query Error: {e}")
        finally:
            conn.close()

        return result

    def get_rental_analysis(self, city, district, address_road):
        stats = {
            "1F_Count": 0, "1F_Min": 0, "1F_Max": 0, "1F_Avg": 0,
            "Upper_Count": 0, "Upper_Avg": 0,
            "Estimated_Range": "無數據",
            "Data_Source_Count": 0
        }
        
        conn = self._get_conn()
        try:
            # rent_data columns: district, address, floor, price_total, price_m2, area_m2
            # 1. Base Query: District
            query = "SELECT * FROM rent_data WHERE district = ?"
            params = [district]
            
            # 2. Road Filtering (Python-side filtering or SQL Like?)
            # SQL LIKE is better
            if address_road:
                # Logic: if Road records > 3, use road. Else use District.
                # Let's count Road records first
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM rent_data WHERE district = ? AND address LIKE ?", [district, f"%{address_road}%"])
                count = cursor.fetchone()[0]
                
                if count >= 3:
                    query += " AND address LIKE ?"
                    params.append(f"%{address_road}%")
                    print(f"✅ [Rent] Using Street-level data: {address_road} ({count} records)")
                else:
                    print(f"⚠️ [Rent] Street-level data sparse ({count}), falling back to District.")

            df = pd.read_sql_query(query, conn, params=params)
            
            if df.empty: return stats
            
            # Price Per Ping Calculation
            # stored price_m2 is unit price. 1 m2 = 0.3025 ping.
            # Price/Ping = Price/m2 / 0.3025
            df['Price_Per_Ping'] = df['price_m2'] / 0.3025
            
            stats['Data_Source_Count'] = len(df)
            
            # Floor Analysis
            mask_1f = df['floor'].astype(str).str.contains('一層|1層')
            df_1f = df[mask_1f]
            df_upper = df[~mask_1f]

            if not df_1f.empty:
                prices = df_1f['Price_Per_Ping']
                stats['1F_Count'] = len(df_1f)
                stats['1F_Avg'] = int(prices.mean())
                
                # Range
                low = int(prices.quantile(0.25))
                high = int(prices.quantile(0.75))
                stats['Estimated_Range'] = f"{low} ~ {high}"
            
            if not df_upper.empty:
                prices = df_upper['Price_Per_Ping']
                stats['Upper_Count'] = len(df_upper)
                stats['Upper_Avg'] = int(prices.mean())
                
                if stats['1F_Count'] < 3:
                     est = int(stats['Upper_Avg'] * 1.6)
                     stats['Estimated_Range'] = f"{int(est*0.9)} ~ {int(est*1.1)} (推估)"

        except Exception as e:
            print(f"Rent Analysis Error: {e}")
        finally:
            conn.close()
            
        return stats
