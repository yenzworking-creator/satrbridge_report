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

        def parse_flow(val):
            try:
                if val is None: return 0
                return float(str(val).replace(',', '').strip())
            except:
                return 0

        # 2025 MRT Data Integration
        if village_stats.get('MRT_Station'):
             mrt_station_name = village_stats.get('MRT_Station')
             mrt_flow_val = self.db_manager.get_mrt_flow(mrt_station_name)
             
             if mrt_flow_val > 0:
                 final_mrt_station = mrt_station_name
                 mrt_status_text = f"鄰近 {mrt_station_name} 站 (2025年10月日均運量 {int(mrt_flow_val)} 人次)"
             else:
                 # Fallback to old logic if not found in 2025 data (e.g. Taipei Metro, not Taoyuan)
                 mrt_flow_val = parse_flow(village_stats.get('MRT_Flow', 0))
                 final_mrt_station = mrt_station_name if mrt_flow_val > 0 else None
                 mrt_status_text = f"鄰近 {final_mrt_station} 站，參考運量約 {int(mrt_flow_val)} 人次" if mrt_flow_val > 0 else "該地點附近無捷運站"
        else:
             mrt_flow_val = 0
             final_mrt_station = None
             mrt_status_text = "該地點附近無捷運站"

        # 4. Construct Payload for MAKE
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
            "decision_context": {
                "strategy_summary": f"User specifically intends to target '{request_data.get('targetCustomers', 'General Public')}' and operate during '{request_data.get('businessHours', 'Standard Hours')}'.",
                "mrt_analysis_instruction": mrt_status_text  # DIRECT INSTRUCTION FOR AI
            },
            # DATA CLEANING: Prevent AI from seeing Station Name if Flow is 0
            "location_data": {**loc_data, "mrt_station": final_mrt_station},
            "market_stats": {
                "mrt_station": final_mrt_station,
                "mrt_flow": mrt_flow_val,
                "mrt_summary": mrt_status_text, # Redundant but safe
                
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
                    
                    # Normalize keys
                    # Expecting 'result' key from formatted JSON or just root
                    if isinstance(result, list):
                        ai_result = result[0] if result else {}
                    else:
                        ai_result = result.get('result') or result

                    # --- DATA NORMALIZATION & FALLBACKS ---
                    # Ensure ROI and Traffic fields exist even if AI names them differently
                    # ROI Aliases
                    if 'roi_period' not in ai_result:
                         ai_result['roi_period'] = (
                             ai_result.get('return_period_months') or 
                             ai_result.get('return_period') or 
                             ai_result.get('roi') or 
                             '-'
                         )
                    
                    # Traffic Aliases & Logic Fallback
                    traffic_val = (
                        ai_result.get('est_daily_traffic') or
                        ai_result.get('daily_traffic') or 
                        ai_result.get('traffic') or 
                        ai_result.get('estimated_traffic') or 
                        ai_result.get('visitors')
                    )

                    if not traffic_val or str(traffic_val) == '-':
                        # Fallback: Calculate from Revenue / AvgConsumption
                        try:
                            rev = float(str(ai_result.get('daily_revenue', '0')).replace(',', '').strip())
                            avg_consume = float(str(request_data.get('avgConsumption', '1')).replace(',', '').strip())
                            if rev > 0 and avg_consume > 0:
                                traffic_val = int(rev / avg_consume * 1.2) # *1.2 adjustment factor for visitors vs paying customers
                            else:
                                traffic_val = '-'
                        except:
                            traffic_val = '-'
                    
                    ai_result['est_daily_traffic'] = traffic_val

                    # INJECT Location Data & API Key & User Decisions for Frontend Use
                    from config import GOOGLE_MAPS_API_KEY
                    if isinstance(ai_result, dict):
                        # Ensure Lat/Lng are present, default to 0 to avoid JS crash, but preferably use loc_data
                        ai_result['lat'] = loc_data.get('lat') or 0
                        ai_result['lng'] = loc_data.get('lng') or 0
                        ai_result['google_maps_key'] = GOOGLE_MAPS_API_KEY
                        # Inject User Input for Confirmation display
                        ai_result['user_target'] = request_data.get('targetCustomers', '一般大眾')
                        ai_result['user_hours'] = request_data.get('businessHours', '未指定')
                    
                    # Return Raw Data for Frontend Dashboard
                    return {
                        "success": True,
                        "raw_data": ai_result,
                        "report_html": "<div>請稍候，正在渲染儀表板...</div>"
                    }

                except json.JSONDecodeError:
                    # MAKE might return "Accepted" OR Invalid JSON (e.g. unescaped newlines)
                    raw_text = response.text.strip()
                    logging.warning(f"MAKE Response JSON Decode Error. Raw: {raw_text[:100]}...")
                    
                    # Heuristic: If it looks like a JSON object, send it to frontend anyway
                    if raw_text.startswith('{') and raw_text.endswith('}'):
                         from config import GOOGLE_MAPS_API_KEY
                         return {
                            "success": True,
                            "raw_data": { 
                                "raw_text_fallback": raw_text,
                                "lat": loc_data.get('lat'),
                                "lng": loc_data.get('lng'),
                                "google_maps_key": GOOGLE_MAPS_API_KEY
                            }, 
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
                # FALLBACK FOR UI TESTING: Return Mock Data if MAKE fails
                from config import GOOGLE_MAPS_API_KEY
                logging.warning("Activating Mock Data due to MAKE failure.")
                return {
                    "success": True, 
                    "raw_data": {
                        "score": 7.8,
                        "summary": "【測試模式】AI 服務暫時無法連線，此為測試數據以供版面檢視。目標客群鎖定精準，人流數據顯示平日與假日皆有穩定客源。建議加強在地行銷。",
                        "daily_revenue": 15000,
                        "rent": 45000,
                        "turnover_rate": 3.5,
                        "return_period_months": 14,
                        "est_daily_traffic": 1200,
                        "target_audience": "上班族 / 學生",
                        "location_type": "住商混合區",
                        "radar_comment": "人流與交通位置優異，但租金成本略高。",
                        "population_body": "該區域方圓 500 公尺內人口密度高，以 25-45 歲青壯年為主。",
                        "rent_body": "周邊店面租金行情約在每坪 2,500 - 3,500 元之間，本案開價合理。",
                        "competition_body": "同業競爭中等，主要競爭對手為連鎖早餐店與便利商店。",
                        "function_body": "鄰近捷運站與公車站，交通便利性極佳。",
                        "space_body": "店面格局方正，建議保留大面窗以增加採光。",
                        "financial_body": "預估首年營收可達 500 萬，淨利率約 15%。",
                        "marketing_body": "建議利用社群媒體進行在地推廣，並提供開幕優惠。",
                        "conclusion_text": "綜合評估為 A 級點位，建議盡快進行議價簽約。",
                        "lat": loc_data.get('lat'),
                        "lng": loc_data.get('lng'),
                        "google_maps_key": GOOGLE_MAPS_API_KEY,
                        "user_target": request_data.get('targetCustomers', '一般大眾'),
                        "user_hours": request_data.get('businessHours', '未指定')
                    },
                    "report_html": "" 
                }

        except Exception as e:
            logging.error(f"Webhook Connection Failed: {e}")
            # FALLBACK FOR UI TESTING (Exception case)
            from config import GOOGLE_MAPS_API_KEY
            return {
                "success": True, 
                "raw_data": {
                    "score": 8.5,
                    "summary": "【連線異常測試】MAKE 連線逾時，顯示模擬數據。此區域具備極高發展潛力。",
                    "daily_revenue": 18000,
                    "rent": 48000,
                    "turnover_rate": 4.0,
                    "return_period_months": 12,
                    "est_daily_traffic": 1500,
                    "lat": loc_data.get('lat'),
                    "lng": loc_data.get('lng'),
                    "google_maps_key": GOOGLE_MAPS_API_KEY,
                    "user_target": request_data.get('targetCustomers', '一般大眾'),
                    "user_hours": request_data.get('businessHours', '未指定')
                },
                "report_html": ""
            }
