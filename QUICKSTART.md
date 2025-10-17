# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Setup Environment (2 minutes)

**Windows:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure Environment Variables (1 minute)

Edit `.env` file with your credentials:

```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_PHONE_NUMBER=+91XXXXXXXXXX
SERVER_URL=your-domain.com
PORT=8000
```

### Step 3: Local Development with ngrok (1 minute)

1. Download and install [ngrok](https://ngrok.com/download)

2. Run ngrok:
```bash
ngrok http 8000
```

3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

4. Update `.env`:
```env
SERVER_URL=abc123.ngrok.io
```
(Note: Don't include `https://`)

### Step 4: Configure Twilio (1 minute)

1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to Phone Numbers → Manage → Active Numbers
3. Select your phone number
4. Under "Voice Configuration":
   - **A CALL COMES IN**: Webhook
   - **URL**: `https://abc123.ngrok.io/incoming-call`
   - **HTTP Method**: POST
5. Save

### Step 5: Start the Server

```bash
# Activate virtual environment
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Start server
python app.py
```

You should see:
```
==================================================
AI Voice Customer Service Agent Starting...
Environment: development
Server URL: abc123.ngrok.io
Port: 8000
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Test Your Agent! 📞

Call your Twilio phone number and start talking!

**Test Conversation:**
```
Agent: "Namaste! Customer support mein aapka swagat hai. How may I help you today?"

You: "Mera order ka status check karo, order ID ABC123"

Agent: "Sure ji, let me check that for you... [fetches order details]"
```

---

## 🧪 Testing Scenarios

### 1. Order Status Inquiry
**Say:** "My order ID is ABC123, status kya hai?"

### 2. Product Availability
**Say:** "Is product ki availability check karo please"

### 3. Transfer to Human
**Say:** "I want to speak to a human agent"

### 4. Create Ticket
**Say:** "Mera order nahi aaya, please help karo"

---

## 🔍 Verify Everything is Working

### Check Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "active_calls": 0,
  "active_sessions": 0,
  "timestamp": "2025-10-17T12:00:00"
}
```

### Check Logs
Watch the console for:
- ✅ `OpenAI session created`
- ✅ `Call started`
- ✅ `Audio streaming...`
- ✅ `Function call: lookup_order`

---

## 📱 Making Your First Test Call

1. **Call the number** from your phone
2. **Wait for greeting** in Hinglish
3. **Speak naturally** - mix Hindi and English
4. **Try these phrases:**
   - "Hello, mujhe help chahiye"
   - "My order number is ABC123"
   - "Status check karo please"
   - "I want to speak to someone"

---

## 🐛 Troubleshooting

### Issue: Call connects but no audio
**Solution:**
- Check OpenAI API key has realtime API access
- Verify ngrok URL is correct in Twilio webhook
- Ensure SERVER_URL in .env matches ngrok URL

### Issue: "Cannot connect to OpenAI"
**Solution:**
- Verify OPENAI_API_KEY is correct
- Check internet connection
- Ensure you have GPT-4o-realtime access

### Issue: WebSocket connection fails
**Solution:**
- Must use HTTPS (ngrok provides this)
- Check firewall settings
- Verify Twilio webhook URL is correct

---

## 📊 Monitor Your Agent

### Active Calls Dashboard
```bash
curl http://localhost:8000/metrics
```

### Get Call Details
```bash
curl http://localhost:8000/call/CA1234567890
```

### View Logs
All events are logged to console in real-time:
```
2025-10-17 12:00:00 - voice_agent - INFO - Call started: CA123
2025-10-17 12:00:05 - voice_agent - INFO - Function call: lookup_order
2025-10-17 12:00:10 - voice_agent - INFO - Call completed - Duration: 45s
```

---

## 🚀 Production Deployment

### Option 1: Railway
```bash
railway login
railway init
railway up
```

### Option 2: Heroku
```bash
heroku create
git push heroku main
heroku config:set OPENAI_API_KEY=sk-...
```

### Option 3: AWS/GCP/Azure
See README.md for detailed deployment guides

---

## 🎯 Next Steps

1. ✅ **Customize Agent Instructions**
   - Edit `config/agent_config.py`
   - Modify greeting messages
   - Add company-specific context

2. ✅ **Add More Functions**
   - Order tracking
   - Payment processing
   - Appointment scheduling

3. ✅ **Connect Real Database**
   - Replace mock data in `database_service.py`
   - Add PostgreSQL/MongoDB
   - Implement real order lookup

4. ✅ **Add Analytics**
   - Call success rate
   - Average handling time
   - Customer satisfaction

---

## 💡 Pro Tips

1. **Use natural Hinglish** - The agent is trained to code-mix naturally
2. **Let customer interrupt** - VAD (Voice Activity Detection) handles this
3. **Clear escalation paths** - Define when to transfer to human
4. **Log everything** - All conversations are stored for analysis
5. **Monitor costs** - Each call costs ~$0.20-0.35 per minute

---

## 📚 Learn More

- [OpenAI Realtime API Docs](https://platform.openai.com/docs/guides/realtime)
- [Twilio Voice Docs](https://www.twilio.com/docs/voice)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🆘 Need Help?

- Check logs in console
- Review README.md
- Test with `/health` endpoint
- Verify all environment variables

**Happy Building! 🎉**
