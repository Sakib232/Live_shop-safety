
# cd /home/sakib/data/AI/yolo_flask_app && source venv/bin/activate && python app.py





# 🏪 Shop Security System - Setup Guide

## How It Works





























1. **Live Monitoring**: Camera monitors your shop continuously
2. **Person Detection**: When someone enters, the system detects them
3. **Email Alert**: You receive an email with a snapshot of who entered
4. **Timestamp**: Each alert includes date/time of the detection

---

## Setup Instructions

### Step 1: Enable Gmail App Password

**You CANNOT use your regular Gmail password.** You need an App Password:

1. Go to: https://myaccount.google.com/apppasswords
2. Make sure 2-Factor Authentication is ON
3. Select:
   - **App**: Mail
   - **Device**: Windows Computer (or your device)
4. Google will generate a 16-character password
5. Copy this password (it will have spaces, ignore them)

### Step 2: Update `.env` File

Edit `.env` file in the `yolo_flask_app` folder:

```env
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASS=abcd efgh ijkl mnop
ALERT_TO=your_email@gmail.com
```

**Example:**
```env
EMAIL_USER=sakib@gmail.com
EMAIL_PASS=abcd efgh ijkl mnop
ALERT_TO=sakib@gmail.com
```

### Step 3: Restart the App

```bash
cd /home/sakib/data/AI/yolo_flask_app
python app.py
```

The app will automatically reload with your email settings.

---

## How to Use for Shop Security

### When You Close the Shop

1. Leave the live camera running at: `http://127.0.0.1:9000/live`
2. Or access from any network: `http://<your-ip>:9000/live`

### When Someone Enters

- 📸 System detects the person
- 📧 Email sent automatically with:
  - Snapshot of the person
  - Date and time
  - Detection confidence
- ⏱️ **Cooldown**: Max 1 email per 2 minutes (prevents spam)

### If No Alert is Coming

Check:
1. ✅ Email credentials in `.env` are correct
2. ✅ App restarted after changing `.env`
3. ✅ Check Gmail inbox (email might go to Spam)
4. ✅ Check live stream shows the camera feed

---

## Settings You Can Adjust

In `.env` file:

- **CONFIDENCE_THRESHOLD**: 0.2 (current) - detects people reliably
  - Lower = more detections (more alerts)
  - Higher = only very clear detections

- **ALERT_COOLDOWN**: 120 seconds
  - Prevents multiple emails from same person
  - Change to 300 for 5 minutes cooldown

---

## Troubleshooting

**Problem**: "Not sending emails"
- Check Gmail credentials are correct
- Try accessing your Gmail from the computer first
- Check if 2-Factor Authentication is enabled

**Problem**: "Too many false alerts"
- Increase ALERT_COOLDOWN to 300 or 600
- Increase CONFIDENCE_THRESHOLD to 0.3 or 0.4

**Problem**: "Missing detections"
- Lower CONFIDENCE_THRESHOLD to 0.15
- Make sure camera has good lighting

---

## Remote Access (Optional)

To access from your phone/other devices:

```bash
# Find your computer IP:
hostname -I
# Example: 192.168.1.100

# Then access from phone:
# http://192.168.1.100:9000/live
```

---

## ⚠️ Important Notes

✅ App runs on `localhost` by default (only local access)
✅ To use remotely, modify `app.py` line: `app.run(host='0.0.0.0', ...)`
✅ Email is sent in background (doesn't freeze the app)
✅ Snapshots saved in `uploads/` folder with timestamps

---

**Need help?** Check the server logs if any errors appear.
