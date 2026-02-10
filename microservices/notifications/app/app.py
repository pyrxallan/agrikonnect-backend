from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Notification Service is running. Use /health or /send.'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'notification-service'}), 200

@app.route('/send', methods=['POST'])
def send_notification():
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'message' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    user_id = data['user_id']
    message = data['message']
    notif_type = data.get('type', 'system')

    # Log the notification (Simulation)
    logger.info(f"Sending {notif_type} to User {user_id}: {message}")

    return jsonify({
        'status': 'sent',
        'recipient': user_id,
        'content': message
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
