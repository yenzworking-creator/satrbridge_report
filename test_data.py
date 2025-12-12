import sys
import logging
from location_service import LocationService
from database_manager import DatabaseManager

# Simple logging
logging.basicConfig(level=logging.ERROR)

def test_data_only():
    print("🚀 啟動數據檢查 (不發送網頁請求)...")
    
    address = "台北市中山區松江路111號"
    print(f"📍 測試地址: {address}")

    # 1. Location
    loc_service = LocationService()
    loc_data = loc_service.get_location_details(address)
    print(f"✅ 定位結果: {loc_data.get('city')} {loc_data.get('district')} {loc_data.get('village')}")

    # 2. Database
    db_manager = DatabaseManager()
    db_manager.load_data_lazily()
    
    village_stats = db_manager.get_village_data(
        loc_data.get('city'), 
        loc_data.get('district'), 
        loc_data.get('village'),
        loc_data.get('mrt_station')
    )
    
    print("-" * 30)
    print("🧪 [測試 1] 自動偵測結果:")
    print(f"人口總數: {village_stats.get('Population')}")
    
    print("-" * 30)
    print("🧪 [測試 2] 強制使用 '松江里' 測試資料庫 (驗證 DB 邏輯):")
    # Force test with correct village to prove DB works
    manual_stats = db_manager.get_village_data(
        loc_data.get('city'), 
        loc_data.get('district'), 
        "松江里", # Explicitly pass correct village
        loc_data.get('mrt_station')
    )
    print(f"強制松江里-男性: {manual_stats.get('Male_Pop')}")
    print(f"強制松江里-納稅戶: {manual_stats.get('Tax_Payers')}")
    print("-" * 30)
    
    if village_stats.get('Male_Pop') == 0:
        print("⚠️ 警告: 男性人口為 0，可能是村里名稱比對不到 (Excel資料落差)")
    else:
        print("✅ 數據擷取成功！")

if __name__ == "__main__":
    test_data_only()
