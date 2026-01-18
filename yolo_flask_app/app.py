import os
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.2))
ALERT_COOLDOWN = 120  # 2 minutes in seconds
PORT = int(os.getenv('PORT', 9000))

# Shop Mode File
SHOP_MODE_FILE = 'shop_mode.json'

# Directories
UPLOAD_FOLDER = 'uploads'
MODEL_PATH = 'yolov8n.pt'  # YOLOv8 Nano - detects persons/people
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Load YOLO model
try:
    model = YOLO(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None

# Email configuration
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
ALERT_TO = os.getenv('ALERT_TO')

# WhatsApp Configuration (Twilio)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')
ALERT_PHONE = os.getenv('ALERT_PHONE')

# Try to import Twilio
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else False
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. WhatsApp alerts disabled. Install with: pip install twilio")

# Anti-spam tracking
last_alert_time = {}
alerts_history = []


def get_shop_mode():
    """Get current shop mode (ON/OFF)."""
    try:
        if os.path.exists(SHOP_MODE_FILE):
            with open(SHOP_MODE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('is_on', False)
    except:
        pass
    return False


def set_shop_mode(is_on):
    """Set shop mode (ON/OFF)."""
    with open(SHOP_MODE_FILE, 'w') as f:
        json.dump({'is_on': is_on, 'updated': datetime.now().isoformat()}, f)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_whatsapp_alert(message, image_path=None):
    """Send WhatsApp alert via Twilio."""
    if not TWILIO_AVAILABLE or not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE, ALERT_PHONE]):
        logger.warning("WhatsApp not configured. Skipping WhatsApp alert.")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send WhatsApp message
        message_obj = client.messages.create(
            body=message,
            from_=f'whatsapp:{TWILIO_PHONE}',
            to=f'whatsapp:{ALERT_PHONE}'
        )
        
        logger.info(f"WhatsApp alert sent successfully: {message_obj.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp alert: {e}")
        return False


def send_alert_email(snapshot_path, timestamp):
    """Send email alert with snapshot when person detected."""
    if not all([EMAIL_USER, EMAIL_PASS, ALERT_TO]):
        logger.warning("Email credentials not configured. Skipping email alert.")
        return False

    try:
        # Check cooldown - max 1 email per ALERT_COOLDOWN seconds
        current_time = time.time()
        if 'last_alert' in last_alert_time:
            if current_time - last_alert_time['last_alert'] < ALERT_COOLDOWN:
                logger.info(f"Alert cooldown active. Skipping email.")
                return False

        # Create email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = ALERT_TO
        msg['Subject'] = '🚨 SHOP SECURITY ALERT: Person Detected!'

        # Email body
        body = f"""
        🚨 SHOP SECURITY ALERT 🚨
        ================================
        
        ⚠️ Someone detected in your shop!
        
        ⏰ Time: {timestamp}
        📍 Location: Shop Camera
        
        A snapshot has been attached for your review.
        
        Detection Confidence: {CONFIDENCE_THRESHOLD * 100:.0f}%
        
        ⚡ Actions:
        1. Review the attached image
        2. Check your shop immediately
        3. Contact authorities if needed
        
        Stay Safe!
        """
        msg.attach(MIMEText(body, 'plain'))

        # Attach snapshot
        if os.path.exists(snapshot_path):
            with open(snapshot_path, 'rb') as attachment:
                image = MIMEImage(attachment.read())
                image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(snapshot_path))
                msg.attach(image)

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        last_alert_time['last_alert'] = current_time
        logger.info("Alert email sent successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
        return False


def detect_owner(frame_or_image_path):
    """
    Run YOLOv8 Face Detection inference and return detection results.
    
    Args:
        frame_or_image_path: numpy array (frame) or path to image
        
    Returns:
        dict: {
            'is_owner': bool (True if face detected),
            'confidence': float,
            'annotated_frame': numpy array,
            'detections': list of detection dicts
        }
    """
    if model is None:
        return {
            'is_owner': False,
            'confidence': 0.0,
            'annotated_frame': None,
            'detections': [],
            'error': 'Model not loaded'
        }

    try:
        # Run inference
        results = model(frame_or_image_path)
        result = results[0]

        # Get detections
        detections = []
        max_confidence = 0.0
        is_owner = False

        if result.boxes is not None:
            for box in result.boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                # Class 0 is 'person' in COCO dataset
                if cls_id == 0:
                    detections.append({
                        'class': 'person',
                        'confidence': conf,
                        'bbox': box.xyxy[0].cpu().numpy().tolist()
                    })
                    max_confidence = max(max_confidence, conf)

        # Check if person detected with confidence >= threshold
        is_owner = max_confidence >= CONFIDENCE_THRESHOLD

        # Get annotated frame
        annotated_frame = result.plot()

        return {
            'is_owner': is_owner,
            'confidence': max_confidence,
            'annotated_frame': annotated_frame,
            'detections': detections
        }

    except Exception as e:
        logger.error(f"Error during inference: {e}")
        return {
            'is_owner': False,
            'confidence': 0.0,
            'annotated_frame': None,
            'detections': [],
            'error': str(e)
        }


@app.route('/')
def index():
    """Main page with upload and live stream options."""
    return render_template('index.html')


@app.route('/admin')
def admin():
    """Admin dashboard for shop mode control."""
    shop_status = get_shop_mode()
    return render_template('admin.html', shop_status=shop_status)


@app.route('/api/shop/status', methods=['GET'])
def get_shop_status():
    """Get current shop status."""
    is_on = get_shop_mode()
    return jsonify({
        'is_on': is_on,
        'status': 'CLOSED - Security ON' if is_on else 'OPEN - Security OFF',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/shop/toggle', methods=['POST'])
def toggle_shop_mode():
    """Toggle shop mode ON/OFF."""
    try:
        data = request.get_json()
        is_on = data.get('is_on', not get_shop_mode())
        set_shop_mode(is_on)
        
        status_msg = '🔒 Shop CLOSED - Security System ACTIVATED' if is_on else '🔓 Shop OPEN - Security System DISABLED'
        logger.info(status_msg)
        
        return jsonify({
            'success': True,
            'is_on': is_on,
            'message': status_msg
        })
    except Exception as e:
        logger.error(f"Error toggling shop mode: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/alerts/history', methods=['GET'])
def get_alerts_history():
    """Get alert history."""
    return jsonify({
        'alerts': alerts_history[-20:],  # Last 20 alerts
        'total': len(alerts_history)
    })


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle image upload and inference."""
    if request.method == 'GET':
        return render_template('upload.html')

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']


    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Use JPG or PNG.'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run inference
        detection_result = detect_owner(filepath)

        if detection_result.get('error'):
            return jsonify({'error': detection_result['error']}), 500

        # Save annotated image
        annotated_frame = detection_result['annotated_frame']
        output_filename = f"annotated_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        cv2.imwrite(output_path, annotated_frame)

        person_detected = detection_result['is_owner']
        confidence = detection_result['confidence']

        # If person detected, send alert (if shop is in secure mode)
        if person_detected:
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            shop_is_closed = get_shop_mode()
            
            if shop_is_closed:
                # Log alert
                alert_entry = {
                    'timestamp': timestamp_str,
                    'confidence': float(confidence),
                    'image': f'/uploads/{output_filename}',
                    'type': 'upload'
                }
                alerts_history.append(alert_entry)
                
                # Send alerts asynchronously
                def send_alerts():
                    send_alert_email(filepath, timestamp_str)
                    send_whatsapp_alert(f"🚨 SECURITY ALERT! Person detected at {timestamp_str}. Confidence: {confidence*100:.1f}%")
                
                threading.Thread(target=send_alerts).start()

        return jsonify({
            'person_detected': person_detected,
            'confidence': float(confidence),
            'message': 'PERSON DETECTED' if person_detected else 'NO PERSON DETECTED',
            'annotated_image': f'/uploads/{output_filename}',
            'original_image': f'/uploads/{filename}',
            'detections': detection_result['detections']
        }), 200

    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/live')
def live():
    """Live webcam streaming page."""
    return render_template('live.html')


def generate_frames():
    """Generate frames from webcam with YOLOv8 inference."""
    cap = cv2.VideoCapture(0)
    
    # If webcam is not available, create a placeholder
    webcam_available = cap.isOpened()
    if not webcam_available:
        logger.warning("Could not open webcam. Using placeholder image.")

    try:
        while True:
            if webcam_available:
                success, frame = cap.read()
                if not success:
                    break
            else:
                # Create a placeholder image
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                frame[:] = (50, 50, 50)  # Dark gray background
                # Add text
                cv2.putText(frame, "No Webcam Connected", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 2)
                cv2.putText(frame, "Please attach a webcam or upload images", (80, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
                time.sleep(0.033)  # ~30 FPS

            # Resize frame for faster inference (optional)
            frame = cv2.resize(frame, (640, 480))

            # Run inference
            detection_result = detect_owner(frame)
            annotated_frame = detection_result['annotated_frame']

            if annotated_frame is None:
                annotated_frame = frame

            # Add status text
            is_owner = detection_result['is_owner']
            confidence = detection_result['confidence']
            status_text = f"OWNER DETECTED (Conf: {confidence:.2f})" if is_owner else f"NOT OWNER (Conf: {confidence:.2f})"
            status_color = (0, 255, 0) if is_owner else (0, 0, 255)
            cv2.putText(
                annotated_frame,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                status_color,
                2
            )
            
            # Add shop mode indicator
            shop_is_closed = get_shop_mode()
            shop_status_text = "🔒 SECURE MODE ON" if shop_is_closed else "🔓 OPEN MODE"
            shop_color = (0, 0, 255) if shop_is_closed else (0, 255, 0)
            cv2.putText(
                annotated_frame,
                shop_status_text,
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                shop_color,
                2
            )

            # If person detected and shop is closed, send alert (with cooldown)
            person_detected = detection_result['is_owner']
            confidence = detection_result['confidence']
            
            if person_detected and confidence > 0 and shop_is_closed:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Save snapshot
                snapshot_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )
                cv2.imwrite(snapshot_path, annotated_frame)
                
                # Check cooldown
                current_time = time.time()
                if 'last_alert' not in last_alert_time or (current_time - last_alert_time['last_alert'] >= ALERT_COOLDOWN):
                    # Log alert
                    alert_entry = {
                        'timestamp': timestamp,
                        'confidence': float(confidence),
                        'image': f'/uploads/{os.path.basename(snapshot_path)}',
                        'type': 'live'
                    }
                    alerts_history.append(alert_entry)
                    
                    # Send alerts asynchronously
                    def send_live_alerts():
                        send_alert_email(snapshot_path, timestamp)
                        send_whatsapp_alert(f"🚨 INTRUDER ALERT! Person detected at {timestamp}. Confidence: {confidence*100:.1f}%")
                    
                    threading.Thread(target=send_live_alerts).start()
                    last_alert_time['last_alert'] = current_time

            # Encode frame to JPEG
            success, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()

            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n' +
                   frame_bytes + b'\r\n')

    finally:
        if webcam_available:
            cap.release()


@app.route('/video_feed')
def video_feed():
    """Video feed endpoint for streaming."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/uploads/<filename>')
def download_file(filename):
    """Serve uploaded/processed files."""
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': f'File too large. Max size: {MAX_FILE_SIZE / (1024*1024):.0f}MB'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"Starting Flask app on port {PORT}...")
    logger.info("🏪 Shop Security System Ready!")
    logger.info(f"📱 Local Access: http://127.0.0.1:{PORT}")
    logger.info(f"📹 Live Camera: http://127.0.0.1:{PORT}/live")
    logger.info(f"📤 Upload Image: http://127.0.0.1:{PORT}/upload")
    app.run(debug=True, host='0.0.0.0', port=PORT, threaded=True)
