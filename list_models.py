import requests
from config import GEMINI_API_KEY
import json

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open("models_list.txt", "w", encoding="utf-8") as f:
            for m in data.get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    f.write(f"{m['name']}\n")
    else:
        print(response.text)
except Exception as e:
    print(e)
