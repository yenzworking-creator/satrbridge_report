import os

# API Keys (User should replace these or set environment variables)
# 建議您將 Key 設定在環境變數中，或者直接貼在這裡 (請小心不要外洩)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyAyFh1GUq4a0YfxEnwKsAdrmkIXWLD351E")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAaZq8bRucXWQvoLQkJUqSCmigUJO3gmGg")

# Email Configuration (Gmail App Password is recommended)
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "zac351595@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "1qaz!@#$1989127")

# Data Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_FILE = os.path.join(DATA_DIR, "village_data.xlsx")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Google Form Configuration (User MUST Update These)
GOOGLE_FORM_ID = os.getenv("GOOGLE_FORM_ID", "1FAIpQLSezy5I9H8gau7bige691iOQgNu_fARFtSPIfMLDMygfh0wNcQ")
GOOGLE_FORM_ENTRY_IDS = {
    "address": "entry.123456",
    "industry": "entry.789012",
    "area": "entry.345678",
    # Add other fields as needed
}

# Report Configuration
REPORT_OUTPUT_DIR = os.path.join(BASE_DIR, "static", "reports")
os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)

# MAKE (Integromat) Webhook Configuration
# 2025-12-10 Updated by User Request
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/tsvjdbqy5b8ytto1vrvlrm4xwjibb2k4"
