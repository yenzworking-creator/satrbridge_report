import logging
import requests
import json
from datetime import datetime
from config import MAKE_WEBHOOK_URL
from location_service import LocationService
from database_manager import DatabaseManager

class ReportService:
    def __init__(self):
        self.loc_service = LocationService()
        self.db_manager = DatabaseManager()
        if not self.db_manager.is_loaded:
            self.db_manager.load_data_lazily()

    def create_report(self, request_data):
        """
        Gather data and trigger MAKE Webhook for report generation.
        """
        address = request_data.get('address')
        logging.info(f"Processing Request for: {address}")

        # 1. Gather Location Data
        loc_data = self.loc_service.get_location_details(address)
        if "error" in loc_data:
            return {"success": False, "message": loc_data['error']}

        # 2. Gather Database Stats
        village_name = loc_data.get('village', 'Unknown')
        village_stats = self.db_manager.get_village_data(
            loc_data.get('city'), 
            loc_data.get('district'), 
            village_name,
            loc_data.get('mrt_station')
        )
        
        # 3. Extra Location Search (Competitors)
        ind_type = request_data.get('industryType', '餐廳')
        if ind_type == '其他': ind_type = '餐廳' # Fallback
        
        # Use simple coordinate distance for nearby search if available
        lat, lng = loc_data.get('lat'), loc_data.get('lng')
        competitor_info = "無定位資料"
        if lat and lng:
            competitor_info = self.loc_service.search_nearby(lat, lng, ind_type)

        # 4. Construct Payload for MAKE
        # We send EVERYTHING so MAKE has full context for AI
        payload = {
            "request_info": {
                "address": address,
                "industry": request_data.get('industryType'),
                "area_size": request_data.get('areaSize'),
                "avg_consumption": request_data.get('avgConsumption'),
                "target_customers": request_data.get('targetCustomers'),
                "business_hours": request_data.get('businessHours'),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            "location_data": loc_data,
            "market_stats": {
                "mrt_station": village_stats.get('MRT_Station'),
                "mrt_flow": village_stats.get('MRT_Flow'),
                
                # Detailed Population
                "population": village_stats.get('Population'),
                "male_pop": village_stats.get('Male_Pop'),
                "female_pop": village_stats.get('Female_Pop'),
                
                # Financial / Tax
                "median_income": village_stats.get('Income_Median'),
                "tax_payers": village_stats.get('Tax_Payers'),
                
                # Rent
                "rent_1f_avg": village_stats.get('1F_Avg'),
                "rent_upper_avg": village_stats.get('Upper_Avg'),
                "rent_data_count": village_stats.get('Data_Source_Count')
            },
            "nearby_info": {
                "parking": loc_data.get('parking_info', '無資料'),
                "schools": loc_data.get('school_info', '無資料'),
                "competitors": competitor_info,
                "functional_index": "生活機能成熟" # Placeholder/Heuristic
            }
        }
        
        # DEBUG: Print payload to console
        print("-" * 50)
        print("🚀 [DEBUG] 正要發送給 MAKE 的資料 (Payload):")
        print(f"Address: {address}")
        print(f"Male Pop: {payload['market_stats'].get('male_pop')}")
        print(f"Tax Payers: {payload['market_stats'].get('tax_payers')}")
        print("-" * 50)
        
        logging.info(f"Sending Payload to MAKE: {json.dumps(payload, ensure_ascii=False)}")

        # 4. Call MAKE Webhook
        try:
            # Short timeout? No, report gen might take a few seconds.
            # MAKE custom webhook waits for response action, so we wait.
            response = requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                # Expecting textual body if MAKE responds nicely, or JSON
                try:
                    # Try parsing JSON first
                    result = response.json()
                    
                    # Normalize keys if MAKE returns different casing
                    pdf_url = result.get('pdf_url') or result.get('pdfUrl') or result.get('file_url')
                    html_preview = result.get('html_preview') or result.get('previewHtml') or result.get('html')
                    
                    # Normalize keys
                    ai_result = result.get('result') or result # Expecting 'result' key from formatted JSON or just root
                    
                    # Return Raw Data for Frontend Dashboard
                    return {
                        "success": True,
                        "raw_data": ai_result,
                        "report_html": "<div>請稍候，正在渲染儀表板...</div>"
                    }

                    return {
                        "success": True,
                        "report_html": html_preview or f"<div><h2>報告已生成</h2><a href='{pdf_url}'>點此下載 PDF</a></div>",
                        "pdf_url": pdf_url
                    }
                    
                except json.JSONDecodeError:
                    # MAKE might return "Accepted" OR Invalid JSON (e.g. unescaped newlines)
                    raw_text = response.text.strip()
                    logging.warning(f"MAKE Response JSON Decode Error. Raw: {raw_text[:100]}...")
                    
                    # Heuristic: If it looks like a JSON object, send it to frontend anyway
                    if raw_text.startswith('{') and raw_text.endswith('}'):
                        return {
                            "success": True,
                            "raw_data": raw_text, # Frontend will try to parse/repair
                            "report_html": "<div>請稍候，正在渲染儀表板 (Raw Mode)...</div>"
                        }

                    # True fallback for non-JSON responses
                    return {
                        "success": True,
                        "message": "請求已接收，正在處理中。",
                        "report_html": f"<div style='text-align:center; padding:2rem;'><h3><i class='fa-solid fa-check'></i> 請求發送成功</h3><p>MAKE 正在生成報告，但回傳格式無法解析。</p><p>MAKE 回傳訊息: {raw_text}</p></div>"
                    }
            else:
                logging.error(f"MAKE Error {response.status_code}: {response.text}")
                return {"success": False, "message": f"MAKE 伺服器錯誤: {response.status_code}"}

        except Exception as e:
            logging.error(f"Webhook Connection Failed: {e}")
            return {"success": False, "message": f"連線失敗: {str(e)}"}
