# In your Python Flask app (app.py or main.py)
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Make sure CORS is enabled

# Your existing root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Cell Site Locator API is running!"
    })

# ADD THIS NEW HEALTH ENDPOINT
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Python ML Backend',
        'message': 'Cell Site Locator API is running!',
        'port': 5000
    }), 200

# ADD THESE SERVICE-SPECIFIC HEALTH CHECKS
@app.route('/api/buildings/health', methods=['GET'])
def buildings_health():
    """Building API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Building Extraction API'
    }), 200

@app.route('/api/cell-site/health', methods=['GET'])
def cellsite_health():
    """Cell Site API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'Cell Site Locator API'
    }), 200

# Your other existing routes...
# @app.route('/api/cell-site/upload', methods=['POST'])
# @app.route('/api/buildings/generate', methods=['POST'])
# etc.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)