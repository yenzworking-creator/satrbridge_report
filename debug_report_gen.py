from report_generator import ReportGenerator
import json

# Mock Data
request_data = {
    "industry": "Coffee Shop",
    "area": 30,
    "avg_price": 150
}

location_data = {
    "address": "Test Address",
    "city": "Taipei",
    "district": "Xinyi",
    "village": "Test Village"
}

village_stats = {
    "MRT_Station": "Taipei 101",
    "MRT_Flow": 50000,
    "Population": 10000,
    "Male_Pop": 4800,
    "Female_Pop": 5200,
    "Income_Median": 800,
    "Estimated_Range": "2000-3000",
    "1F_Avg": 2500,
    "Upper_Avg": 1500,
    "Data_Source_Count": 5
}

print("Initialize Generator...")
gen = ReportGenerator()
if not gen.api_key:
    print("Error: API Key missing or model init failed.")
else:
    print("Generating Report...")
    result = gen.generate_report(request_data, location_data, village_stats)
    
    print("\n--- RAW RESULT KEY CHECK ---")
    print(f"Keys found: {list(result.keys())}")
    
    print("\n--- FULL RESULT ---")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if "error" in result:
        print(f"\nCRITICAL ERROR FOUND: {result['error']}")
