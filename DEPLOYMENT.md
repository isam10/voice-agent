# Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Environment Configuration ✓
- [ ] All environment variables set correctly
- [ ] OPENAI_API_KEY verified (with realtime access)
- [ ] TWILIO credentials verified
- [ ] SERVER_URL points to production domain
- [ ] LOG_LEVEL set to INFO or WARNING (not DEBUG)
- [ ] ENVIRONMENT set to "production"

### 2. Security Hardening ✓
- [ ] `.env` file NOT committed to git
- [ ] Twilio webhook signature validation enabled
- [ ] Rate limiting implemented on endpoints
- [ ] HTTPS/SSL certificate configured
- [ ] CORS origins restricted (not allow all)
- [ ] API keys rotated if exposed during development
- [ ] Input validation on all user inputs

### 3. Code Quality ✓
- [ ] All tests passing (`pytest tests/`)
- [ ] No syntax errors or import issues
- [ ] Error handling comprehensive
- [ ] Logging configured properly
- [ ] No hardcoded credentials
- [ ] Code reviewed

### 4. Infrastructure ✓
- [ ] Server/hosting platform selected
- [ ] Domain name configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Auto-scaling enabled (if applicable)
- [ ] Backup strategy defined
- [ ] Monitoring tools set up

### 5. Database ✓
- [ ] Production database configured
- [ ] Connection pooling enabled
- [ ] Backup schedule configured
- [ ] Migration scripts ready
- [ ] Indexes optimized
- [ ] Access credentials secured

### 6. Twilio Configuration ✓
- [ ] Phone number purchased
- [ ] Webhook URL updated to production
- [ ] Status callback URL configured
- [ ] Geographic permissions set
- [ ] Call recording configured (if required)
- [ ] Budget alerts set up

### 7. OpenAI Configuration ✓
- [ ] API key for production environment
- [ ] Rate limits understood
- [ ] Billing limits set
- [ ] Usage alerts configured
- [ ] Model version pinned

### 8. Monitoring & Logging ✓
- [ ] Application logs centralized
- [ ] Error tracking (Sentry/DataDog) configured
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring configured
- [ ] Alert notifications set up
- [ ] Dashboard created for metrics

### 9. Testing ✓
- [ ] End-to-end tests completed
- [ ] Load testing performed
- [ ] Concurrent call handling verified
- [ ] Error scenarios tested
- [ ] Failover tested
- [ ] Audio quality verified

### 10. Documentation ✓
- [ ] README.md updated
- [ ] API documentation complete
- [ ] Deployment guide written
- [ ] Troubleshooting guide available
- [ ] Team trained on system
- [ ] Runbook created

---

## Deployment Steps

### Step 1: Prepare Code
```bash
# Run tests
pytest tests/ -v

# Check for errors
python -m py_compile app.py

# Update dependencies
pip freeze > requirements.txt
```

### Step 2: Setup Server

**AWS EC2 Example:**
```bash
# SSH into server
ssh ubuntu@your-server-ip

# Clone repository
git clone https://github.com/your-repo/voice-agent.git
cd voice-agent

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Create .env file
nano .env

# Paste production values
OPENAI_API_KEY=sk-prod-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+91...
SERVER_URL=yourdomain.com
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 4: Setup SSL (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com
```

### Step 5: Configure Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/voice-agent
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/voice-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Setup Systemd Service
```ini
# /etc/systemd/system/voice-agent.service
[Unit]
Description=AI Voice Customer Service Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/voice-agent
Environment="PATH=/home/ubuntu/voice-agent/venv/bin"
ExecStart=/home/ubuntu/voice-agent/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-agent
sudo systemctl start voice-agent
sudo systemctl status voice-agent
```

### Step 7: Configure Twilio Webhook
1. Go to Twilio Console
2. Update webhook URL to: `https://yourdomain.com/incoming-call`
3. Set method to POST
4. Save

### Step 8: Test Production
```bash
# Health check
curl https://yourdomain.com/health

# Make test call
# Call your Twilio number
```

### Step 9: Monitor
```bash
# View logs
sudo journalctl -u voice-agent -f

# Check metrics
curl https://yourdomain.com/metrics
```

---

## Post-Deployment

### Immediate Actions
- [ ] Make test call to verify functionality
- [ ] Check logs for errors
- [ ] Verify metrics are being collected
- [ ] Test all function calls (order lookup, transfer, etc.)
- [ ] Confirm Hinglish conversation flows naturally
- [ ] Test concurrent calls (5+ simultaneous)

### First 24 Hours
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify cost tracking
- [ ] Review customer feedback
- [ ] Check server resources (CPU, memory)
- [ ] Validate all integrations working

### First Week
- [ ] Analyze call metrics
- [ ] Review conversation logs
- [ ] Identify improvement areas
- [ ] Optimize agent instructions if needed
- [ ] Scale infrastructure if needed
- [ ] Update documentation with learnings

---

## Rollback Plan

If issues occur:

1. **Immediate Rollback**
   ```bash
   sudo systemctl stop voice-agent
   # Switch Twilio webhook back to previous URL
   ```

2. **Restore Previous Version**
   ```bash
   git checkout previous-stable-tag
   sudo systemctl restart voice-agent
   ```

3. **Emergency Contact**
   - Have backup phone number for human agents
   - Update Twilio to route to backup system

---

## Scaling Strategy

### Horizontal Scaling
- Use load balancer (AWS ALB, Nginx)
- Deploy multiple instances
- Shared Redis for session state

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Enable caching

### Cost Optimization
- Monitor per-call costs
- Set daily budget limits
- Optimize conversation length
- Cache frequent queries

---

## Maintenance Schedule

### Daily
- Check error logs
- Monitor active calls
- Review cost reports

### Weekly
- Analyze call quality
- Review conversation transcripts
- Update agent instructions
- Check security logs

### Monthly
- Rotate API keys
- Update dependencies
- Review and optimize costs
- Performance tuning
- Backup verification

---

## Emergency Contacts

**Technical Issues:**
- DevOps Team: [contact]
- Backend Team: [contact]

**Service Issues:**
- Twilio Support: support.twilio.com
- OpenAI Support: help.openai.com

**Business:**
- Product Manager: [contact]
- Customer Success: [contact]

---

## Success Metrics

Track these KPIs:

1. **Availability**: Target 99.9% uptime
2. **Response Time**: < 500ms for audio streaming
3. **Call Success Rate**: > 95%
4. **Transfer Rate**: < 20%
5. **Customer Satisfaction**: > 4.0/5.0
6. **Cost per Call**: < $0.35
7. **Average Call Duration**: 2-5 minutes
8. **Concurrent Call Capacity**: 50+

---

## Congratulations! 🎉

Your AI Voice Customer Service Agent is now live in production!

Monitor closely for the first few days and iterate based on real-world usage.
