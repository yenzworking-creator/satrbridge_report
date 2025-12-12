import googlemaps
from config import GOOGLE_MAPS_API_KEY

class LocationService:
    def __init__(self):
        if not GOOGLE_MAPS_API_KEY or "YOUR_KEY" in GOOGLE_MAPS_API_KEY:
             print("警告: 未設定 Google Maps API Key")
             self.gmaps = None
        else:
            self.gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    def get_location_details(self, address):
        if not self.gmaps: 
            return {"error": "API Key missing"}

        try:
            # 1. Geocoding
            geocode_result = self.gmaps.geocode(address, language='zh-TW')
            if not geocode_result: 
                 return {"error": "找不到該地址"}

            result = geocode_result[0]
            loc = result['geometry']['location']
            lat, lng = loc['lat'], loc['lng']
            
            # 2. Extract Admin Area
            city, district, village = "", "", ""
            for comp in result.get('address_components', []):
                types = comp.get('types', [])
                name = comp.get('long_name', "")
                if 'administrative_area_level_1' in types: city = name
                if 'administrative_area_level_2' in types and ('市' in name or '縣' in name): city = name
                if 'administrative_area_level_2' in types and '區' in name: district = name
                if 'administrative_area_level_3' in types and ('區' in name or '鄉' in name or '鎮' in name): district = name
                if 'administrative_area_level_4' in types and ('里' in name or '村' in name): village = name
                if 'neighborhood' in types and ('里' in name or '村' in name): village = name

            # Fallback for Village parsing
            # If Geocoding didn't return village (common for street addresses), try Reverse Geocoding with Lat/Lng
            if not village and lat and lng:
                print("📍 正向定位未回傳村里，嘗試反向定位 (Reverse Geocoding)...")
                try:
                    reverse_results = self.gmaps.reverse_geocode((lat, lng), language='zh-TW')
                    if reverse_results:
                        # DEBUG: Print Raw Components of first result
                        print(f"🐛 [Geo Raw] First Result Components: {reverse_results[0].get('address_components')}")
                        
                        # Iterate through results to find the most granular admin level
                        for r in reverse_results:
                            # DEBUG: Print all types to see what we get
                            # print(f"DEBUG ADDR: {r.get('formatted_address')}") 
                            for comp in r.get('address_components', []):
                                types = comp.get('types', [])
                                name = comp.get('long_name', "")
                                
                                # Check if this component IS a village
                                # Google sometimes puts Village (Li) at Level 3 in Taiwan vs standard Level 4
                                check_types = ['administrative_area_level_4', 'neighborhood', 'administrative_area_level_3']
                                is_village_level = any(t in types for t in check_types)
                                has_village_char = '里' in name or '村' in name
                                
                                if is_village_level and has_village_char:
                                    # Prefer Traditional Chinese if possible (usually longer results or standard)
                                    # But for now just take the first one found, or maybe check if we already have one
                                    # The Simplified '朱园里' appears first. We might want to fix this later but let's just get IT first.
                                    village = name
                                    # Normalize: Google sometimes returns Simplified '园' or '台' despite zh-TW
                                    village = village.replace('园', '園').replace('台', '臺')
                                    print(f"📍 反向定位成功，找到村里: {village}")
                                    break
                                
                                # Debug print for relevant levels
                                if 'administrative_area' in str(types):
                                    print(f"   [Debug Geo] Found: {name} ({types})")
                                    
                            if village: break
                except Exception as e:
                    print(f"反向定位失敗: {e}")

            if not village and ('里' in address or '村' in address):
                # Simple extraction from address string if API failed to categorize it
                import re
                match = re.search(r'(\w+[村里])', address)
                if match: village = match.group(0)

            print(f"📍 最終定位: {city} {district} {village} ({lat}, {lng})")
            
            # 3. Find Nearby MRT

            print(f"📍 定位: {city} {district} {village} ({lat}, {lng})")
            
            # 3. Find Nearby MRT
            # Google Places API - Search for 'subway_station' within 1km
            mrt_station = "無捷運"
            try:
                places = self.gmaps.places_nearby(
                    location=(lat, lng), 
                    radius=1000, 
                    type='subway_station',
                    language='zh-TW'
                )
                if places.get('results'):
                    # Get the closest one
                    mrt_station = places['results'][0]['name']
                    # Remove "捷運" or "站" for cleaner matching with Excel? 
                    # Usually "捷運台電大樓站" -> Data might use "台電大樓" or "台電大樓站"
                    print(f"🚝 最近捷運: {mrt_station}")
            except Exception as e:
                print(f"捷運搜尋失敗: {e}")

            # 4. Nearby Facilities Search
            # We fetch simple text summaries for MAKE AI to process
            parking_info = self._get_nearby_summary(lat, lng, 'parking', '停車場')
            school_info = self._get_nearby_summary(lat, lng, 'school', '學校')
            
            # 5. Competitors (Dynamic via request?) 
            # Ideally this comes from the caller, but we can do a generic 'restaurant' or 'store' search here 
            # or let report_service pass the industry term. 
            # For now, we'll expose a method to search specifically or just return a general "store" search if not specified.
            # actually report_service.py calls get_location_details with just address.
            # We will refactor to allow passing 'keyword' or just provide helper method.
            
            return {
                "address": result.get('formatted_address', address),
                "lat": lat, 
                "lng": lng,
                "city": city,
                "district": district,
                "village": village,
                "mrt_station": mrt_station,
                "parking_info": parking_info,
                "school_info": school_info
            }

        except Exception as e:
            print(f"Location Error: {e}")
            return {"error": str(e)}

    def search_nearby(self, lat, lng, keyword, radius=500):
        """Public method to search specific keyword"""
        return self._get_nearby_summary(lat, lng, 'point_of_interest', keyword, radius)

    def _get_nearby_summary(self, lat, lng, place_type, keyword, radius=500):
        if not self.gmaps: return "無資料"
        try:
            places = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                keyword=keyword, # type is often too broad, keyword is better
                language='zh-TW'
            )
            val = []
            if places.get('results'):
                for p in places['results'][:5]: # Top 5
                    name = p.get('name')
                    rating = p.get('rating', 'N/A')
                    dist = "約500m內" # Google Places Nearby doesn't return distance directly without geometry calc
                    val.append(f"{name}({rating}★)")
            return "、".join(val) if val else "周邊無相關設施"
        except Exception as e:
            return f"查詢錯誤: {str(e)}"
