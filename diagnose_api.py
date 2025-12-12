import requests
from config import GEMINI_API_KEY
import json

def test_generate():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Hello, are you working?"}]}]
    }
    
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        print(f"Status: {response.status_code}")
        print("Response Snippet:", response.text[:200])
        
        if response.status_code != 200:
            # Try Pro
            print("\nTrying Gemini Pro...")
            url_pro = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            response_pro = requests.post(url_pro, headers={"Content-Type": "application/json"}, json=payload)
            print(f"Status Pro: {response_pro.status_code}")
            print("Response Snippet:", response_pro.text[:200])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate()
