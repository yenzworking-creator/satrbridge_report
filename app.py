from flask import Flask, render_template, request, jsonify
from report_service import ReportService
from database_manager import DatabaseManager
import threading
import logging
from whitenoise import WhiteNoise

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s')

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')

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
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e), "trace": traceback.format_exc()}), 500

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Internal Server Error",
        "error": str(error)
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "success": False,
        "message": "Resource Not Found",
        "error": str(error)
    }), 404

if __name__ == '__main__':
    # Start loading thread
    t = threading.Thread(target=background_load)
    t.start()
    
    print("🚀 網頁伺服器啟動中...請稍候...")
    app.run(debug=True, port=5000, use_reloader=False) 
    # use_reloader=False to avoid running init code twice and messing up threads
