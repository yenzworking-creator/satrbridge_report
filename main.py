from database_manager import DatabaseManager
from location_service import LocationService
from report_generator import ReportGenerator
from email_service import EmailService

def main(request_data):
    print("=== 店面選址評估系統啟動 ===")
    
    # 1. Initialize Modules
    db_manager = DatabaseManager()
    loc_service = LocationService()
    report_gen = ReportGenerator()
    email_service = EmailService()

    # 2. Get Location Details
    address = request_data.get('address')
    print(f"正在定位地址: {address}...")
    loc_data = loc_service.get_location_details(address)
    
    if "error" in loc_data:
        print(f"定位失敗: {loc_data['error']}")
        return

    village_name = loc_data.get('village')
    if not village_name:
        print("注意: 無法從地址中精確識別村里名稱，將嘗試僅用行政區查詢或忽略村里數據。")
    
    # 3. Query Database
    print(f"正在查詢資料庫: {loc_data.get('city')} {loc_data.get('district')} {village_name}...")
    village_stats = db_manager.get_village_data(
        loc_data.get('city'), 
        loc_data.get('district'), 
        village_name
    )
    
    if village_stats:
        print("已找到該區域詳細數據！")
    else:
        print("資料庫中無此區域詳細數據，將由 AI 進行通用評估。")

    # 4. Generate AI Report
    print("正在生成 AI 評估報告 (請稍候)...")
    report = report_gen.generate_report(request_data, loc_data, village_stats)
    
    print("\n" + "="*30)
    print("REPORT PREVIEW:")
    print(report[:500] + "...\n(truncated)")
    print("="*30 + "\n")

    # 5. Send Email
    email = request_data.get('email')
    print(f"正在寄送報告至: {email}...")
    email_service.send_report(email, report)
    
    print("=== 流程結束 ===")

if __name__ == "__main__":
    # Test Data Simulation
    # 這裡模擬從表單接收到的資料
    test_request = {
        "email": "test@example.com",
        # 請確保這裡使用測試資料庫中存在的地址以驗證匹配功能
        "address": "台北市大安區龍泉里師大路", 
        "industry": "咖啡廳",
        "area": 25,
        "avg_price": 150
    }
    
    # 如果您設定了 main.py 的執行，它會使用測試資料跑一次流程
    main(test_request)
