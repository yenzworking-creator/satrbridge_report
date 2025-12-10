import requests
import json

url = "http://127.0.0.1:5000/evaluate"
data = {
    "email": "test@example.com",
    "address": "台北市大安區新生南路三段",
    "industry": "咖啡廳",
    "area": 30,
    "avg_price": 150
}

try:
    print("Sending request...")
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n--- REPORT DATA KEYS ---")
        report_data = result.get('report_data', {})
        print(report_data.keys())
        
        print("\n--- CHECKING RISK ANALYSIS ---")
        print(report_data.get('risk_analysis'))
        
        print("\n--- CHECKING DUE DILIGENCE ---")
        print(report_data.get('due_diligence'))
        
        print("\n--- CHECKING HTML ---")
        html = result.get('report_html', '')
        print(f"HTML Length: {len(html)}")
        if len(html) < 500:
            print("WARNING: HTML seems too short.")
            print(html)
        
        # Save HTML for review
        with open("test_report_output.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved test_report_output.html")
    else:
        print("Error:", response.text)

except Exception as e:
    print(f"Request failed: {e}")
