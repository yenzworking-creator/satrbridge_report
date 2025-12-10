import requests
import json

url = "http://127.0.0.1:5000/api/evaluate"
data = {
    "address": "台北市信義區信義路五段7號", 
    "email": "test@example.com",
    "industry": "Cafe",
    "area": 30,
    "avg_price": 200
}

try:
    print("Sending request...")
    res = requests.post(url, json=data)
    print(f"Status: {res.status_code}")
    print("Response JSON:")
    print(res.json())
except Exception as e:
    print(f"Error: {e}")
