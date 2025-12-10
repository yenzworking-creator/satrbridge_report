from flask import Flask, render_template, request, jsonify
from database_manager import DatabaseManager
from location_service import LocationService
from report_generator import ReportGenerator
from email_service import EmailService
import re
import threading

from report_service import ReportService

app = Flask(__name__)

# Initialize Modules
# DatabaseManager will prompt loading but we can trigger it in background
db_manager = DatabaseManager()
report_service = ReportService()

# Pre-load data in a separate thread so app startup isn't blocked 
# but request will wait if not ready
def background_load():
    db_manager.load_data_lazily()

@app.route('/')
def index():
    return render_template('assessment_form.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        print(f"🚀 收到評估請求: {data.get('address')}")
        
        # Use new ReportService which handles Location, DB, AI, and File Gen
        result = report_service.create_report(data)
        
        return jsonify(result)

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # Start loading thread
    t = threading.Thread(target=background_load)
    t.start()
    
    print("🚀 網頁伺服器啟動中...請稍候...")
    app.run(debug=True, port=5000, use_reloader=False) 
    # use_reloader=False to avoid running init code twice and messing up threads
