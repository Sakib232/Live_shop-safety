

# YOLOv8 Owner Detection Flask Web Application

A complete Flask web application for real-time owner detection using YOLOv8. Upload images or stream from your webcam to detect if an owner is present. Automatically sends email alerts when unknown persons are detected.

## Features

- **Image Upload Detection**: Upload JPG/PNG images for instant YOLOv8 inference
- **Live Webcam Streaming**: Real-time detection from your laptop camera (MJPEG stream)
- **Smart Alerts**: Email notifications with snapshots when owner is not detected
- **Confidence Threshold**: Configurable detection threshold (default 60%)
- **Anti-Spam Protection**: Maximum 1 email alert per 2 minutes
- **Security Validation**: File type and size validation
- **Beautiful UI**: Modern responsive web interface
- **Annotated Results**: Bounding boxes and confidence scores displayed

## Project Structure

```
yolo_flask_app/
├── app.py                 # Flask application with all routes
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── README.md             # This file
├── templates/
│   ├── index.html        # Home page
│   ├── upload.html       # Image upload page
│   └── live.html         # Live webcam page
├── static/
│   └── style.css         # Styling
├── uploads/              # Uploaded/processed images
└── models/
    └── best.pt           # YOLOv8 model (you need to place this)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Webcam (for live streaming)
- Gmail account with App Password (for email alerts)

### 2. Clone/Download and Navigate

```bash
cd yolo_flask_app
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables

Copy `.env.example` to `.env` and fill in your details:

```bash
cp .env.example .env
```

Edit `.env`:

```env
PORT=9000
CONFIDENCE_THRESHOLD=0.6

# Gmail Configuration
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
ALERT_TO=recipient@example.com
```

#### Getting Gmail App Password:

1. Enable 2-Factor Authentication on your Google Account
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Select "Mail" and "Windows Computer" (or your OS)
4. Copy the generated 16-character password
5. Paste it as `EMAIL_PASS` in `.env`

### 6. Place Model File

Copy your trained `best.pt` to the `models/` folder:

```bash
cp /path/to/your/best.pt models/best.pt
```

Or update the `MODEL_PATH` in `app.py` if your model is elsewhere.

### 7. Run the Application

```bash
python app.py
```
# run this project 

 cd /home/sakib/data/AI/yolo_flask_app && source venv/bin/activate && python app.py



You should see:
```
Starting Flask app on port 9000...
 * Running on http://127.0.0.1:9000
```

### 8. Open in Browser

Open your browser and navigate to:
```
http://127.0.0.1:9000
```

## Usage Guide

### Image Upload

1. Click "Upload Image" on the home page
2. Select or drag-drop a JPG/PNG file (max 10MB)
3. View original and annotated images with detection results
4. If unknown person detected:
   - Message shows "NOT OWNER"
   - Alert email is sent automatically (max 1 per 2 minutes)

### Live Webcam Streaming

1. Click "Live Webcam" on the home page
2. Camera feed starts streaming with real-time detection
3. Real-time inference runs on each frame
4. Status shows "OWNER DETECTED" or "NOT OWNER" with confidence score
5. Alerts are triggered when unknown persons detected (with cooldown)

## Configuration

### Confidence Threshold

Edit in `.env`:
```env
CONFIDENCE_THRESHOLD=0.6
```

Or in `app.py`, line 28:
```python
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))
```

### Alert Cooldown

Edit in `app.py`, line 30:
```python
ALERT_COOLDOWN = 120  # 2 minutes in seconds
```

### Port

Change in `.env`:
```env
PORT=9000
```

### Max Upload Size

Edit in `app.py`, line 25:
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

## API Endpoints

### GET `/`
Home page with upload and live stream options

### GET `/upload`
Upload page

### POST `/upload`
Upload image and run inference
- **Form Data**: `file` (JPG/PNG)
- **Response**: JSON with detection results

### GET `/live`
Live streaming page

### GET `/video_feed`
MJPEG video stream from webcam
- **Content-Type**: `multipart/x-mixed-replace`

### GET `/uploads/<filename>`
Serve uploaded/processed files

## Troubleshooting

### Webcam not working
- Check if another app is using the camera
- Try using `cv2.VideoCapture(1)` instead of `0` in `app.py` line 176

### Email not sending
- Verify Gmail App Password is correct
- Enable "Less secure app access" if using regular Gmail password (not recommended)
- Check that `ALERT_TO` email is valid
- Look for error logs in terminal

### Model not loading
- Verify `models/best.pt` exists
- Check file path in `app.py` (line 39)
- Ensure model is in correct YOLOv8 format

### Slow inference
- Reduce frame size (edit line 154 in `app.py`)
- Use GPU if available (YOLOv8 will auto-detect)
- Lower confidence threshold to process fewer detections

### Memory issues
- Clear `uploads/` folder periodically (old images)
- Reduce streaming resolution

## Security Notes

1. **Never commit `.env`** - it contains sensitive information
2. **Use App Passwords**, not your main Google password
3. **Change PORT** from default 9000 if deploying publicly
4. **Add authentication** if exposed to internet
5. **Use HTTPS** in production
6. **Validate all inputs** - already done in this app

## Performance Tips

- Webcam streaming uses MJPEG (good balance of speed/quality)
- Inference runs on CPU by default (GPU if available)
- Frames are resized to 640x480 for faster processing
- Alert cooldown prevents email spam

## File Size Limits

- **Upload**: Max 10MB per image
- **Uploads folder**: No automatic cleanup (monitor disk space)

## Logging

Logs are printed to console. To save logs:

```python
# In app.py, after line 14:
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## License

This project is provided as-is for educational and personal use.

## Support

For issues with:
- **YOLOv8**: See [docs.ultralytics.com](https://docs.ultralytics.com)
- **Flask**: See [flask.palletsprojects.com](https://flask.palletsprojects.com)
- **OpenCV**: See [opencv.org](https://opencv.org)

## Next Steps

To enhance this application:

1. Add database to track detections
2. Implement user authentication
3. Add scheduling (alerts only during certain hours)
4. Integrate with cloud storage for snapshots
5. Add face recognition for verified owners
6. Build mobile app with REST API
7. Deploy with Docker/Kubernetes
8. Add frontend analytics dashboard

Enjoy your YOLOv8 detection system!
