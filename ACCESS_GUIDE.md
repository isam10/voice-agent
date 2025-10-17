# 🌐 How to Access Your Voice Assistant Server

## ❌ INCORRECT URLs (Won't Work in Browser)

These addresses are used internally by the server but **cannot be accessed** in a browser:
- ❌ `http://0.0.0.0:8000` - This is the binding address (all network interfaces)
- ❌ `http://0.0.0.0:8000/docs` - Won't work

**Error**: `ERR_ADDRESS_INVALID` or "can't reach this page"

---

## ✅ CORRECT URLs (Use These!)

### For Local Access (Same Computer)

Use **localhost** or **127.0.0.1**:

#### Main Endpoints
- ✅ **Root/Status**: http://localhost:8000
- ✅ **API Documentation**: http://localhost:8000/docs
- ✅ **Health Check**: http://localhost:8000/health
- ✅ **Metrics**: http://localhost:8000/metrics

#### Alternative (Same Result)
- ✅ **Root/Status**: http://127.0.0.1:8000
- ✅ **API Documentation**: http://127.0.0.1:8000/docs
- ✅ **Health Check**: http://127.0.0.1:8000/health
- ✅ **Metrics**: http://127.0.0.1:8000/metrics

---

## 🖥️ Quick Access Commands

### Open in Browser (Windows)
```powershell
# Open main page
start http://localhost:8000

# Open API documentation
start http://localhost:8000/docs

# Open health check
start http://localhost:8000/health
```

### Test from PowerShell
```powershell
# Test root endpoint
curl http://localhost:8000

# Test health check
curl http://localhost:8000/health

# Test metrics
curl http://localhost:8000/metrics

# Get formatted JSON
Invoke-RestMethod http://localhost:8000/health | ConvertTo-Json
```

---

## 📱 For External Access (Other Devices)

### On Your Local Network

Find your computer's IP address:
```powershell
# Get your local IP
ipconfig | Select-String "IPv4"
```

Example output: `192.168.1.100`

Then access from other devices on the same network:
- `http://192.168.1.100:8000`
- `http://192.168.1.100:8000/docs`

### For Internet Access (Testing)

Use **ngrok** to expose your local server:

```powershell
# Install ngrok from https://ngrok.com/download

# Start ngrok
ngrok http 8000

# You'll get a URL like:
# https://abc123.ngrok.io
```

Then anyone can access:
- `https://abc123.ngrok.io`
- `https://abc123.ngrok.io/docs`

---

## 🔍 Understanding the Addresses

### Server Binding Address: `0.0.0.0:8000`
- **What it means**: Server listens on ALL network interfaces
- **Can you browse to it?**: ❌ NO
- **Why not?**: `0.0.0.0` is a special address meaning "all interfaces", not a specific one

### Localhost: `localhost` or `127.0.0.1`
- **What it means**: Your own computer (loopback interface)
- **Can you browse to it?**: ✅ YES
- **When to use**: When accessing from the same computer where server is running

### Local Network IP: `192.168.x.x` or `10.x.x.x`
- **What it means**: Your computer's address on your local network
- **Can you browse to it?**: ✅ YES (from any device on same network)
- **When to use**: Accessing from other devices (phone, tablet, another computer)

### Public IP: Via ngrok or cloud hosting
- **What it means**: Accessible from anywhere on the internet
- **Can you browse to it?**: ✅ YES (from anywhere)
- **When to use**: Testing with Twilio, sharing with others

---

## 🎯 What Each Endpoint Shows

### 1. Root Endpoint
**URL**: http://localhost:8000

**Response**:
```json
{
  "status": "AI Voice Agent Running",
  "version": "1.0.0",
  "service": "Real-Time Speech-to-Speech Customer Service",
  "languages": ["English", "Hindi", "Hinglish"]
}
```

---

### 2. API Documentation (Swagger UI)
**URL**: http://localhost:8000/docs

**Shows**:
- Interactive API documentation
- All available endpoints
- Test each endpoint directly
- Request/response examples
- Schema definitions

**Features**:
- Click "Try it out" to test endpoints
- See request formats
- View response schemas
- Test authentication

---

### 3. Health Check
**URL**: http://localhost:8000/health

**Response**:
```json
{
  "status": "healthy",
  "active_calls": 0,
  "active_sessions": 0,
  "openai_sessions": 0,
  "timestamp": "2025-10-17T12:00:00.000000",
  "environment": "development"
}
```

---

### 4. Metrics
**URL**: http://localhost:8000/metrics

**Response**:
```json
{
  "active_calls": 0,
  "active_sessions": 0,
  "openai_sessions": 0,
  "timestamp": "2025-10-17T12:00:00.000000"
}
```

---

## 🚀 Recommended Workflow

### Step 1: Start Server
```powershell
cd d:\voice-assistant
python app.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 2: Open Browser
Open any of these in your browser:
- http://localhost:8000/docs (Swagger UI - Best for testing)
- http://localhost:8000/health (Health check)
- http://localhost:8000 (Status page)

### Step 3: Test API
Use Swagger UI at http://localhost:8000/docs to:
1. Explore all endpoints
2. Test each endpoint
3. See request/response formats

---

## 🛠️ Troubleshooting

### Issue: "Can't reach this page" or ERR_ADDRESS_INVALID
**Problem**: Using `0.0.0.0` in browser  
**Solution**: Use `localhost` or `127.0.0.1` instead

### Issue: "Connection refused"
**Problem**: Server not running  
**Solution**: 
```powershell
cd d:\voice-assistant
python app.py
```

### Issue: Different computer can't connect
**Problem**: Firewall or wrong IP  
**Solution**:
1. Get your IP: `ipconfig`
2. Allow port 8000 in Windows Firewall
3. Use `http://YOUR-IP:8000`

### Issue: "This site can't provide a secure connection"
**Problem**: Browser expecting HTTPS  
**Solution**: Use `http://` (not `https://`) for local development

---

## 📋 Quick Reference

| What You Want | URL to Use |
|---------------|------------|
| **View API Docs** | http://localhost:8000/docs |
| **Check Health** | http://localhost:8000/health |
| **View Metrics** | http://localhost:8000/metrics |
| **Test Locally** | http://localhost:8000 |
| **Share Publicly** | Use ngrok: https://abc123.ngrok.io |
| **Twilio Webhook** | https://your-ngrok-url.ngrok.io/incoming-call |

---

## 💡 Pro Tips

1. **Always use localhost** when testing locally
2. **Use ngrok** for Twilio webhook testing
3. **Check Swagger UI** at `/docs` for full API documentation
4. **Monitor health** at `/health` endpoint
5. **Bookmark** http://localhost:8000/docs for easy access

---

**Remember**: 
- ✅ `localhost:8000` = Works in browser
- ❌ `0.0.0.0:8000` = Doesn't work in browser
- ✅ `127.0.0.1:8000` = Works in browser (same as localhost)

---

**Your server is running! Access it at**: http://localhost:8000/docs
