# 🏪 Complete Shop Security System - Setup Guide

## ✅ System is READY!

Your complete shop security system is now running with all features:

### 📋 Features Implemented:

1. ✅ **ON/OFF Shop Mode Control**
   - Toggle security on when shop is CLOSED
   - Turn off alerts when shop is OPEN

2. ✅ **Real-Time Person Detection**
   - YOLOv8 AI-powered detection
   - Works 24/7 on live camera feed
   - Detects people from any angle

3. ✅ **Email Alerts**
   - Instant email with person snapshot
   - Timestamp included
   - Confidence level shown

4. ✅ **WhatsApp Alerts** (Optional)
   - SMS-like WhatsApp messages to your phone
   - Instant notification with detection info

5. ✅ **Admin Dashboard**
   - View shop status (OPEN/CLOSED)
   - Control security mode
   - See recent security alerts
   - View alert history

---

## 🚀 Quick Start

### Access Points:

- **🏠 Home:** http://192.168.8.110:9000
- **⚙️ Admin Control:** http://192.168.8.110:9000/admin
- **📹 Live Camera:** http://192.168.8.110:9000/live
- **📤 Upload Test:** http://192.168.8.110:9000/upload

---

## 📧 Email Configuration (REQUIRED)

### Steps:

1. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Ensure 2-Factor Authentication is ON
   - Select: Mail + Windows Computer
   - Copy the 16-character password

2. **Update `.env` file:**
   ```
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=xxxx xxxx xxxx xxxx
   ALERT_TO=your_email@gmail.com
   ```

3. **Restart the app:**
   ```bash
   cd /home/sakib/data/AI/yolo_flask_app
   python app.py
   ```

---

## 📱 WhatsApp Configuration (OPTIONAL)

### To enable WhatsApp alerts:

1. **Create Twilio Account:**
   - Go to: https://www.twilio.com
   - Sign up (free trial with $15 credit)
   - Get verified number

2. **Get WhatsApp Number:**
   - Link WhatsApp Business Account to Twilio
   - Get your Twilio WhatsApp number

3. **Update `.env`:**
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE=+1234567890
   ALERT_PHONE=+92XXXXXXXXXX
   ```

4. **Restart app**

---

## 🎮 How to Use

### When You CLOSE Your Shop:

1. Go to: http://192.168.8.110:9000/admin
2. Click: **🔒 Close Shop - Turn ON Security**
3. Status changes to: "CLOSED - Security ON"
4. System starts monitoring

### When Someone Enters:

- 🚨 **Instant detection** of any person
- 📧 **Email sent** with person snapshot
- 📱 **WhatsApp sent** with alert message
- 🔔 **Alert logged** in admin panel

### When You OPEN Your Shop:

1. Go to: http://192.168.8.110:9000/admin
2. Click: **🔓 Open Shop - Turn OFF Security**
3. Status changes to: "OPEN - Security OFF"
4. No more alerts sent

---

## 📊 Admin Dashboard Features:

### Status Display:
- 🟢 **GREEN** = OPEN (Security OFF)
- 🔴 **RED** = CLOSED (Security ON)

### Control Panel:
- One-click buttons to toggle mode
- Instant status update

### Alert History:
- View last 20 alerts
- Click image to enlarge
- See confidence percentage
- Timestamp for each alert

---

## 🎥 Live Camera View:

### Shows:
- Real-time video feed (640x480)
- Person detection boxes
- Confidence scores
- Shop status indicator
- AI detection info

### Access:
- From home or anywhere
- Works on phone/tablet
- Auto-reconnect if connection lost

---

## ⚙️ Settings You Can Adjust:

In `.env` file:

```env
# Detection sensitivity (0.0-1.0)
CONFIDENCE_THRESHOLD=0.2
# Lower = more detections
# Higher = only clear detections

# Alert spam prevention (seconds)
ALERT_COOLDOWN=120
# Max 1 email per 120 seconds

# Port (usually 9000)
PORT=9000
```

---

## 🔒 Security Tips:

✅ **Keep credentials secure** - Don't share `.env` file
✅ **Secure your network** - Use strong WiFi password
✅ **Test system** - Upload a photo first to verify setup
✅ **Check email spam folder** - Alerts might go there initially
✅ **Monitor alerts** - Review history regularly

---

## 📞 Troubleshooting

**Problem:** Emails not arriving
- ✓ Check `.env` credentials are correct
- ✓ Check Gmail spam folder
- ✓ Check app is restarted
- ✓ Test with /upload page first

**Problem:** WhatsApp not working
- ✓ Verify Twilio credentials in `.env`
- ✓ Check account has credit
- ✓ Verify phone numbers with country code

**Problem:** No detections
- ✓ Lower CONFIDENCE_THRESHOLD to 0.15
- ✓ Ensure good lighting
- ✓ Keep camera clear of obstructions

**Problem:** Too many false alerts
- ✓ Increase CONFIDENCE_THRESHOLD to 0.3
- ✓ Increase ALERT_COOLDOWN to 300+

---

## 📱 Remote Access

You can access from anywhere on your network:

```
http://192.168.8.110:9000/admin
```

Or from phone on same WiFi:
```
http://192.168.8.110:9000/live
```

---

## 🆘 Need Help?

Check the terminal for logs:
```bash
cd /home/sakib/data/AI/yolo_flask_app
python app.py
```

Look for error messages and check configuration.

---

## 📝 System Status

✅ **Model:** YOLOv8 (Person Detection)
✅ **Server:** Running on port 9000
✅ **Email:** Ready (awaiting credentials)
✅ **WhatsApp:** Ready (awaiting Twilio credentials)
✅ **Live Stream:** Active
✅ **Admin Panel:** Active
✅ **Alert History:** Active

---

## 🎯 Next Steps:

1. Configure Email (REQUIRED)
2. Configure WhatsApp (OPTIONAL)
3. Test with upload page
4. Go live with your shop!

**Your system is ready to protect your shop! 🛡️**
