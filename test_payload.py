import sys
import json
import logging
from report_service import ReportService

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_payload():
    print("🚀 啟動獨立測試腳本 (Standalone Payload Test)...")
    
    # Initialize Service
    try:
        service = ReportService()
        print("✅ ReportService 初始化成功")
    except Exception as e:
        print(f"❌ 初始化失敗: {e}")
        return

    # Mock Request Data
    mock_request = {
        "address": "台北市中山區松江路111號", # Ensure this address exists/works
        "industryType": "咖啡廳",
        "areaSize": 30,
        "avgConsumption": 150,
        "targetCustomers": "上班族",
        "businessHours": "08:00-20:00"
    }

    print(f"📍 測試地址: {mock_request['address']}")
    
    # Call create_report (which now has debug prints)
    # Note: create_report calls the Webhook. We want to intercept or just see the prints.
    # Our modified report_service.py prints the payload BEFORE sending.
    
    try:
        # We don't care about the actual webhook result here, we just want to see the logs
        print("⏳ 正在執行資料蒐集與 Payload 建構...")
        result = service.create_report(mock_request)
        print("✅ 執行完成")
        print("Result:", result)
    except Exception as e:
        print(f"❌ 執行失敗: {e}")

if __name__ == "__main__":
    test_payload()
