# Real-Time Speech-to-Speech AI Voice Customer Service Agent

A production-ready AI voice customer service agent that handles incoming and outgoing phone calls in Hinglish (Hindi-English code-mixing), processes multiple simultaneous calls, and integrates with OpenAI's GPT-4o-realtime API.

## Features

- ✅ Real-time bidirectional audio streaming
- ✅ Hinglish (Hindi-English code-mixing) support
- ✅ Multiple simultaneous call handling
- ✅ OpenAI GPT-4o-realtime integration
- ✅ Twilio Programmable Voice integration
- ✅ Function calling for order lookup, transfers, tickets
- ✅ Production-ready error handling and logging
- ✅ Async/await optimized for performance

## Technology Stack

- **Backend**: FastAPI (Python 3.10+)
- **AI Engine**: OpenAI GPT-4o-realtime-preview API
- **Telephony**: Twilio Programmable Voice
- **WebSocket**: Native Python websockets
- **Async**: asyncio for concurrent call handling

## Project Structure

```
voice-assistant/
├── .env                      # Environment variables
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── app.py                  # Main application
├── config/
│   ├── __init__.py
│   ├── agent_config.py     # Agent configuration & instructions
│   └── settings.py         # Environment settings
├── services/
│   ├── __init__.py
│   ├── openai_service.py   # OpenAI integration
│   ├── twilio_service.py   # Twilio integration
│   └── database_service.py # Database operations
├── models/
│   ├── __init__.py
│   └── call_session.py     # Call session models
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   └── helpers.py          # Helper functions
└── tests/
    ├── __init__.py
    └── test_agent.py       # Unit tests
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- OpenAI API account with GPT-4o-realtime access
- Twilio account with Programmable Voice
- ngrok or production server with HTTPS

### Installation

1. **Clone the repository**
   ```bash
   cd d:\voice-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Edit `.env` file with your credentials:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxx
   TWILIO_ACCOUNT_SID=ACxxxxx
   TWILIO_AUTH_TOKEN=xxxxx
   TWILIO_PHONE_NUMBER=+91XXXXXXXXXX
   SERVER_URL=your-domain.com
   PORT=8000
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

### Twilio Configuration

1. **Purchase a Phone Number**
   - Log into Twilio Console
   - Navigate to Phone Numbers → Buy a Number
   - Select a number with Voice capabilities

2. **Configure Webhook**
   - Go to Phone Numbers → Manage → Active Numbers
   - Select your number
   - Under "Voice Configuration":
     - A CALL COMES IN: Webhook
     - URL: `https://your-domain.com/incoming-call`
     - HTTP Method: POST

3. **Test with ngrok (Development)**
   ```bash
   ngrok http 8000
   ```
   Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   Update Twilio webhook: `https://abc123.ngrok.io/incoming-call`

## Running the Application

### Development Mode

```bash
python app.py
```

Or with uvicorn:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Call Flow

1. Start the server
2. Expose via ngrok (development)
3. Call your Twilio number
4. Agent should greet you in Hinglish
5. Test various scenarios:
   - Ask about order status
   - Request product information
   - Ask to speak with human agent
   - Create support ticket

### Function Testing

The agent supports these function calls:

- **lookup_order**: "Mera order ID ABC123 hai, status kya hai?"
- **check_product_availability**: "Is product ki availability check karo"
- **transfer_to_human**: "I want to speak to a human agent"
- **create_ticket**: "Ek complaint ticket banao"

## API Endpoints

### GET `/`
Health check endpoint
```json
{
  "status": "AI Voice Agent Running",
  "version": "1.0.0"
}
```

### GET `/health`
System health status
```json
{
  "status": "healthy",
  "active_calls": 3,
  "timestamp": "2025-10-17T12:00:00"
}
```

### POST `/incoming-call`
Twilio webhook for incoming calls (returns TwiML)

### WebSocket `/media-stream`
Bidirectional audio streaming endpoint

### POST `/outbound-call`
Initiate outbound calls (implementation pending)

## Deployment

### Option 1: Railway

1. Install Railway CLI
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables in Railway dashboard
5. Deploy: `railway up`

### Option 2: AWS EC2

1. Launch Ubuntu instance
2. Install Python 3.10+
3. Clone repository
4. Install dependencies
5. Configure nginx reverse proxy
6. Set up SSL with Let's Encrypt
7. Run with systemd service

### Option 3: Google Cloud Run

```bash
gcloud run deploy voice-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key with GPT-4o-realtime access | Yes |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Yes |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Yes |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number | Yes |
| `SERVER_URL` | Public domain/URL of server | Yes |
| `PORT` | Server port (default: 8000) | No |
| `ENVIRONMENT` | development/production | No |
| `LOG_LEVEL` | INFO/DEBUG/WARNING/ERROR | No |

## Cost Estimates

### OpenAI GPT-4o-realtime
- Audio input: $100 / 1M tokens (~$0.06/min)
- Audio output: $200 / 1M tokens (~$0.12/min)
- **Estimated**: $0.18 - $0.30 per minute

### Twilio
- Phone number: ~$1/month
- Incoming calls: $0.0085/min (US)
- **Estimated**: $0.01 per minute

**Total per call**: ~$0.20 - $0.35 per minute

## Monitoring & Logging

All events are logged with structured logging:

- Call start/end events
- Audio stream status
- Function executions
- Errors and exceptions
- Performance metrics

Recommended monitoring tools:
- **Sentry**: Error tracking
- **DataDog**: Performance monitoring
- **CloudWatch/StackDriver**: Infrastructure logs

## Troubleshooting

### Issue: WebSocket connection fails

**Solution**: 
- Ensure HTTPS is enabled (required for WSS)
- Check firewall allows WebSocket connections
- Verify SERVER_URL in .env is correct

### Issue: No audio from agent

**Solution**:
- Check OpenAI API key has realtime access
- Verify audio format configuration (g711_ulaw)
- Review OpenAI logs for errors

### Issue: Agent not responding in Hinglish

**Solution**:
- Review `agent_config.py` instructions
- Test with explicit Hinglish prompts
- Check conversation logs

### Issue: Multiple calls fail

**Solution**:
- Increase server resources
- Check async task limits
- Monitor memory usage
- Scale horizontally

## Security Considerations

- ✅ Environment variables not committed
- ✅ Webhook signature validation (implement in production)
- ✅ Rate limiting on endpoints
- ✅ Input sanitization
- ✅ Secure WebSocket (WSS) connections
- ✅ API key rotation policy

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- GitHub Issues
- Email: support@example.com

## Roadmap

- [ ] Outbound calling implementation
- [ ] Redis session management
- [ ] Call recording and playback
- [ ] Analytics dashboard
- [ ] Multi-language support (Tamil, Telugu, etc.)
- [ ] SMS integration
- [ ] CRM integration
- [ ] Advanced sentiment analysis

---

**Built with ❤️ for seamless Hinglish customer support**
