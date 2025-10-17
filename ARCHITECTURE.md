# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI VOICE CUSTOMER SERVICE AGENT                        │
│                     Real-Time Speech-to-Speech with Hinglish                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                              CALL FLOW                                        │
└──────────────────────────────────────────────────────────────────────────────┘

    Customer                Twilio                  Our Server              OpenAI
    📱 Phone              ☎️ Cloud               🖥️ FastAPI            🤖 GPT-4o
       │                      │                        │                      │
       │  1. Call            │                        │                      │
       ├──────────────────>  │                        │                      │
       │  +91XXXXXXXXX       │                        │                      │
       │                      │                        │                      │
       │                      │  2. Webhook Request   │                      │
       │                      │  POST /incoming-call  │                      │
       │                      ├──────────────────────>│                      │
       │                      │                        │                      │
       │                      │  3. TwiML Response    │                      │
       │                      │  <Connect><Stream>    │                      │
       │                      │<──────────────────────┤                      │
       │                      │                        │                      │
       │                      │  4. WebSocket Open    │                      │
       │                      │  WSS /media-stream    │                      │
       │                      ├──────────────────────>│                      │
       │                      │                        │                      │
       │                      │                        │  5. Create Session  │
       │                      │                        ├──────────────────>  │
       │                      │                        │  realtime.connect   │
       │                      │                        │                      │
       │                      │                        │  6. Configure Agent │
       │                      │                        ├──────────────────>  │
       │                      │                        │  session.update     │
       │                      │                        │  (Hinglish instruct)│
       │                      │                        │                      │
       │                      │                        │  7. Initial Greeting│
       │                      │                        │<──────────────────  │
       │                      │                        │  audio stream       │
       │                      │                        │                      │
       │  8. Greeting         │  <---- Audio ------   │                      │
       │  "Namaste! How may   │                        │                      │
       │   I help you?"       │                        │                      │
       │<─────────────────────┤                        │                      │
       │                      │                        │                      │
       │  9. Customer Speech  │  ----- Audio ------>  │                      │
       │  "Mera order ABC123  │                        │                      │
       │   ka status?"        │                        │  10. Send Audio     │
       ├──────────────────────┤                        ├──────────────────>  │
       │                      │                        │  input_audio_buffer │
       │                      │                        │                      │
       │                      │                        │  11. Process & VAD  │
       │                      │                        │      (Understanding)│
       │                      │                        │                      │
       │                      │                        │  12. Function Call  │
       │                      │                        │<──────────────────  │
       │                      │                        │  lookup_order(ABC123)
       │                      │                        │                      │
       │                      │  13. Execute Function │                      │
       │                      │  (Database Query)     │                      │
       │                      │                        │                      │
       │                      │  14. Function Result  │                      │
       │                      │                        ├──────────────────>  │
       │                      │                        │  {order: delivered} │
       │                      │                        │                      │
       │                      │                        │  15. Generate Reply │
       │                      │                        │<──────────────────  │
       │                      │                        │  audio response     │
       │                      │                        │                      │
       │  16. Agent Response  │  <---- Audio ------   │                      │
       │  "Sure ji, aapka     │                        │                      │
       │   order delivered!"  │                        │                      │
       │<─────────────────────┤                        │                      │
       │                      │                        │                      │
       │  ... Conversation continues with natural turn-taking ...            │
       │                      │                        │                      │
       │  17. End Call        │                        │                      │
       ├──────────────────────┤                        │                      │
       │                      │  18. Stop Event       │                      │
       │                      ├──────────────────────>│                      │
       │                      │                        │                      │
       │                      │                        │  19. Close Session  │
       │                      │                        ├──────────────────>  │
       │                      │                        │                      │
       │                      │                        │  20. Log & Cleanup  │
       │                      │                        │  (Save to DB)       │
       │                      │                        │                      │


┌──────────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM COMPONENTS                                     │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI APPLICATION                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           app.py                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │   HTTP       │  │  WebSocket   │  │   Async      │             │   │
│  │  │   Endpoints  │  │   Handler    │  │   Tasks      │             │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Services Layer                               │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │   OpenAI     │  │   Twilio     │  │   Database   │             │   │
│  │  │   Service    │  │   Service    │  │   Service    │             │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Data Models                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │   Call       │  │   Ticket     │  │   Order      │             │   │
│  │  │   Session    │  │   Model      │  │   Model      │             │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Utilities                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │   │
│  │  │   Logger     │  │   Helpers    │  │   Config     │             │   │
│  │  │   Setup      │  │   Functions  │  │   Manager    │             │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW DIAGRAM                                    │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Customer   │
    │   Speaking   │
    └───────┬──────┘
            │ Audio (μ-law 8kHz)
            ▼
    ┌──────────────┐
    │    Twilio    │
    │   Streaming  │
    └───────┬──────┘
            │ Base64 Audio
            │ WebSocket
            ▼
    ┌──────────────┐
    │   FastAPI    │◄──────── Configuration
    │  WebSocket   │          (Agent Instructions)
    │   Handler    │
    └───────┬──────┘
            │ Forward Audio
            ▼
    ┌──────────────┐
    │   OpenAI     │
    │  Realtime    │
    │     API      │
    └───────┬──────┘
            │
            ├─────────► Transcription (Internal)
            │
            ├─────────► Understanding & Intent
            │
            ├─────────► Function Call Decision
            │           (if needed)
            ▼
    ┌──────────────┐
    │  Function    │
    │  Execution   │──────► Database Query
    │  (Tool Use)  │──────► API Call
    └───────┬──────┘──────► Business Logic
            │
            │ Result
            ▼
    ┌──────────────┐
    │   OpenAI     │
    │  Generate    │
    │   Response   │
    └───────┬──────┘
            │ Audio Stream
            ▼
    ┌──────────────┐
    │   FastAPI    │
    │   Forward    │
    └───────┬──────┘
            │ Base64 Audio
            ▼
    ┌──────────────┐
    │    Twilio    │
    │   Playback   │
    └───────┬──────┘
            │ Audio (μ-law 8kHz)
            ▼
    ┌──────────────┐
    │   Customer   │
    │   Hearing    │
    └──────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                         CONCURRENT CALL HANDLING                              │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────────────────────────────┐
    │              FastAPI Server (Async I/O)                     │
    │                                                              │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
    │  │   Call 1    │  │   Call 2    │  │   Call 3    │  ...   │
    │  │  Session    │  │  Session    │  │  Session    │        │
    │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
    │         │                 │                 │                │
    │         ▼                 ▼                 ▼                │
    │  ┌──────────────────────────────────────────────┐          │
    │  │        Active Sessions Dictionary             │          │
    │  │  {call_sid: {ws, openai_ws, metadata}}       │          │
    │  └──────────────────────────────────────────────┘          │
    │                                                              │
    │  Each call has independent:                                 │
    │  • WebSocket connection to Twilio                           │
    │  • WebSocket connection to OpenAI                           │
    │  • Async task for audio streaming                           │
    │  • Conversation context                                     │
    │  • Session state                                            │
    └────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                         FUNCTION CALLING FLOW                                 │
└──────────────────────────────────────────────────────────────────────────────┘

    Customer: "Mera order ABC123 ka status?"
              ↓
    OpenAI Realtime: [Detects intent]
              ↓
    Function Call: lookup_order(order_id="ABC123")
              ↓
    ┌─────────────────────────────────────────┐
    │     execute_tool() in app.py            │
    │  ┌───────────────────────────────────┐  │
    │  │ 1. Parse function name & args     │  │
    │  │ 2. Route to appropriate service   │  │
    │  │ 3. Execute business logic         │  │
    │  │ 4. Query database                 │  │
    │  │ 5. Format response                │  │
    │  └───────────────────────────────────┘  │
    └────────────────┬────────────────────────┘
                     ↓
    Result: {order_id: "ABC123", status: "Delivered", ...}
              ↓
    OpenAI Realtime: [Generates natural response]
              ↓
    Agent: "Sure ji, aapka order ABC123 deliver ho gaya hai!"


┌──────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT ARCHITECTURE                               │
└──────────────────────────────────────────────────────────────────────────────┘

                    Internet
                       ↕
              ┌────────────────┐
              │  Load Balancer │
              │   (Optional)   │
              └───────┬────────┘
                      ↕
        ┌─────────────┴─────────────┐
        │                           │
    ┌───▼────┐                 ┌───▼────┐
    │ Server │                 │ Server │
    │   1    │                 │   2    │
    │        │                 │        │
    │ FastAPI│                 │ FastAPI│
    │  App   │                 │  App   │
    └───┬────┘                 └───┬────┘
        │                          │
        └──────────┬───────────────┘
                   ↕
         ┌─────────────────┐
         │    Database     │
         │  (PostgreSQL/   │
         │    MongoDB)     │
         └─────────────────┘
                   ↕
         ┌─────────────────┐
         │   Redis Cache   │
         │  (Session Mgmt) │
         └─────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                         MONITORING & OBSERVABILITY                            │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌────────────────────────────────────────┐
    │       FastAPI Application              │
    └────┬──────────┬──────────┬─────────────┘
         │          │          │
         ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │  Logs  │ │Metrics │ │ Errors │
    │        │ │        │ │        │
    └────┬───┘ └───┬────┘ └───┬────┘
         │         │          │
         ▼         ▼          ▼
    ┌─────────────────────────────┐
    │    Monitoring Platform      │
    │  • Sentry (Errors)          │
    │  • DataDog (APM)            │
    │  • CloudWatch (Logs)        │
    └─────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   Dashboard    │
         │  • Call Volume │
         │  • Success Rate│
         │  • Latency     │
         │  • Costs       │
         └────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                       │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │ 1. Network Layer                                      │
    │    • HTTPS/TLS encryption                            │
    │    • WSS (Secure WebSocket)                          │
    │    • Firewall rules                                  │
    └──────────────────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────────────────┐
    │ 2. Application Layer                                  │
    │    • Environment variable isolation                  │
    │    • No hardcoded credentials                        │
    │    • Input validation (Pydantic)                     │
    └──────────────────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────────────────┐
    │ 3. API Layer                                         │
    │    • Twilio signature validation                     │
    │    • Rate limiting                                   │
    │    • API key rotation                                │
    └──────────────────────────────────────────────────────┘
                         ↓
    ┌──────────────────────────────────────────────────────┐
    │ 4. Data Layer                                        │
    │    • Sensitive data masking                          │
    │    • Encrypted at rest                               │
    │    • Access control                                  │
    └──────────────────────────────────────────────────────┘
```

## Key Architecture Highlights

### 1. Async Non-Blocking
- All I/O operations are async
- Multiple calls handled concurrently
- No blocking on network operations

### 2. Event-Driven
- WebSocket for real-time communication
- Event handlers for different message types
- Reactive to both customer and AI agent

### 3. Modular Design
- Services isolated by responsibility
- Easy to test and mock
- Can swap implementations

### 4. Scalable
- Stateless application design
- Can add more instances
- Session state can move to Redis

### 5. Observable
- Comprehensive logging
- Metrics at every layer
- Easy debugging and monitoring
