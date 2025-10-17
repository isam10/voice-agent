"""
Main Application - AI Voice Customer Service Agent
FastAPI application with WebSocket support for real-time voice streaming
"""

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Optional, Any
import traceback

# Application imports
from config.settings import settings
from config.agent_config import AGENT_CONFIG, AUDIO_CONFIG
from services.openai_service import OpenAIService
from services.twilio_service import TwilioService
from services.database_service import DatabaseService
from models.call_session import CallSession, CallStatus, CallDirection, OutboundCallRequest
from utils.logger import setup_logger, get_call_logger
from utils.helpers import sanitize_phone_number, generate_session_id, estimate_call_cost

# Setup logger
logger = setup_logger("voice_agent", level=settings.LOG_LEVEL)

# Active sessions storage
active_sessions: Dict[str, Dict[str, Any]] = {}

# Initialize services (will be set in lifespan)
openai_service = None
twilio_service = None
db_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global openai_service, twilio_service, db_service
    
    # Startup
    logger.info("=" * 50)
    logger.info("AI Voice Customer Service Agent Starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Server URL: {settings.SERVER_URL}")
    logger.info(f"Port: {settings.PORT}")
    logger.info("=" * 50)
    
    # Initialize services
    openai_service = OpenAIService(api_key=settings.OPENAI_API_KEY)
    twilio_service = TwilioService(
        account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN,
        phone_number=settings.TWILIO_PHONE_NUMBER
    )
    db_service = DatabaseService()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close all active sessions
    for call_sid in list(active_sessions.keys()):
        try:
            await cleanup_session(call_sid)
        except Exception as e:
            logger.error(f"Error cleaning up session {call_sid}: {e}")
    
    # Close database connections
    if db_service:
        await db_service.close()
    
    logger.info("Application shut down complete")


# Initialize app with lifespan
app = FastAPI(
    title="AI Voice Customer Service Agent",
    description="Real-time speech-to-speech AI agent with Hinglish support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "AI Voice Agent Running",
        "version": "1.0.0",
        "service": "Real-Time Speech-to-Speech Customer Service",
        "languages": ["English", "Hindi", "Hinglish"]
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    active_calls = await db_service.get_active_calls_count()
    
    return {
        "status": "healthy",
        "active_calls": active_calls,
        "active_sessions": len(active_sessions),
        "openai_sessions": openai_service.active_session_count,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """
    Twilio webhook for incoming calls
    Returns TwiML to connect call to WebSocket
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        call_status = form_data.get("CallStatus")
        
        logger.info(f"Incoming call: {call_sid} from {from_number} (status: {call_status})")
        
        # Generate WebSocket stream URL
        stream_url = f"wss://{settings.SERVER_URL}/media-stream"
        
        # Generate TwiML
        twiml = twilio_service.generate_connect_twiml(
            stream_url=stream_url,
            call_sid=call_sid,
            from_number=from_number
        )
        
        logger.info(f"TwiML generated for call {call_sid}")
        
        return Response(content=twiml, media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        logger.error(traceback.format_exc())
        
        # Return error TwiML
        error_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>We are experiencing technical difficulties. Please try again later.</Say></Response>'
        return Response(content=error_twiml, media_type="application/xml")


@app.websocket("/media-stream")
async def media_stream_handler(websocket: WebSocket):
    """
    Handle bidirectional audio streaming between Twilio and OpenAI
    """
    await websocket.accept()
    
    call_sid = None
    stream_sid = None
    openai_ws = None
    call_logger = None
    
    logger.info("WebSocket connection established")
    
    try:
        # Create OpenAI session
        session_id = generate_session_id()
        openai_ws = await openai_service.create_session(session_id)
        
        logger.info(f"OpenAI session created: {session_id}")
        
        # Send initial greeting
        await openai_service.send_initial_greeting(openai_ws)
        
        async def twilio_to_openai():
            """Forward audio from Twilio to OpenAI"""
            nonlocal call_sid, stream_sid, call_logger
            
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    event_type = data.get("event")
                    
                    if event_type == "start":
                        # Call started
                        start_data = data.get("start", {})
                        call_sid = start_data.get("callSid")
                        stream_sid = start_data.get("streamSid")
                        
                        # Setup call logger
                        call_logger = get_call_logger(call_sid)
                        call_logger.info("Call started")
                        
                        # Extract call details
                        custom_params = start_data.get("customParameters", {})
                        from_number = custom_params.get("from", "")
                        
                        # Create session record
                        active_sessions[call_sid] = {
                            "call_sid": call_sid,
                            "stream_sid": stream_sid,
                            "openai_session_id": session_id,
                            "openai_ws": openai_ws,
                            "start_time": datetime.utcnow(),
                            "from_number": from_number
                        }
                        
                        # Create database record
                        await db_service.create_call_record(call_sid, start_data)
                        
                        call_logger.info(f"Session initialized - Stream: {stream_sid}")
                    
                    elif event_type == "media":
                        # Audio data from Twilio
                        media_data = data.get("media", {})
                        audio_payload = media_data.get("payload")
                        
                        if audio_payload and openai_ws:
                            # Forward to OpenAI
                            await openai_service.send_audio(openai_ws, audio_payload)
                    
                    elif event_type == "mark":
                        # Mark event (for synchronization)
                        if call_logger:
                            call_logger.debug(f"Mark event: {data.get('mark', {}).get('name')}")
                    
                    elif event_type == "stop":
                        # Call ended
                        if call_logger:
                            call_logger.info("Call ended by Twilio")
                        
                        # Update database
                        if call_sid:
                            await db_service.end_call_record(call_sid)
                        
                        break
            
            except WebSocketDisconnect:
                if call_logger:
                    call_logger.warning("Twilio WebSocket disconnected")
                else:
                    logger.warning(f"Twilio WebSocket disconnected: {call_sid}")
            
            except Exception as e:
                if call_logger:
                    call_logger.error(f"Error in twilio_to_openai: {e}")
                    call_logger.error(traceback.format_exc())
                else:
                    logger.error(f"Error in twilio_to_openai: {e}")
        
        async def openai_to_twilio():
            """Forward responses from OpenAI to Twilio"""
            nonlocal call_logger
            
            try:
                async for event in openai_ws:
                    event_type = event.get("type")
                    
                    # Audio response from assistant
                    if event_type == "response.audio.delta":
                        audio_delta = event.get("delta", "")
                        
                        if stream_sid and audio_delta:
                            # Forward to Twilio
                            await websocket.send_json({
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_delta
                                }
                            })
                    
                    # Audio response completed
                    elif event_type == "response.audio.done":
                        if call_logger:
                            call_logger.debug("Audio response completed")
                    
                    # Transcript for logging
                    elif event_type == "conversation.item.created":
                        item = event.get("item", {})
                        
                        if call_sid:
                            await db_service.log_conversation(call_sid, item)
                        
                        # Log transcript
                        if call_logger and item.get("type") == "message":
                            role = item.get("role", "")
                            content = item.get("content", [])
                            
                            if content:
                                text = content[0].get("transcript", "") if content[0].get("type") == "audio" else content[0].get("text", "")
                                if text:
                                    call_logger.info(f"{role.upper()}: {text[:100]}")
                    
                    # Function call initiated
                    elif event_type == "response.function_call_arguments.done":
                        function_name = event.get("name")
                        call_id = event.get("call_id")
                        arguments_str = event.get("arguments", "{}")
                        
                        if call_logger:
                            call_logger.info(f"Function call: {function_name}")
                        
                        try:
                            arguments = json.loads(arguments_str)
                            
                            # Execute function
                            result = await execute_tool(function_name, arguments, call_sid)
                            
                            if call_logger:
                                call_logger.info(f"Function result: {result}")
                            
                            # Send result back to OpenAI
                            await openai_service.send_function_result(
                                openai_ws,
                                call_id,
                                result
                            )
                        
                        except json.JSONDecodeError as e:
                            if call_logger:
                                call_logger.error(f"Failed to parse function arguments: {e}")
                            
                            # Send error result
                            await openai_service.send_function_result(
                                openai_ws,
                                call_id,
                                {"error": "Invalid arguments"}
                            )
                        
                        except Exception as e:
                            if call_logger:
                                call_logger.error(f"Function execution error: {e}")
                            
                            # Send error result
                            await openai_service.send_function_result(
                                openai_ws,
                                call_id,
                                {"error": str(e)}
                            )
                    
                    # Response completed
                    elif event_type == "response.done":
                        if call_logger:
                            call_logger.debug("Response generation completed")
                    
                    # Error from OpenAI
                    elif event_type == "error":
                        error_info = event.get("error", {})
                        if call_logger:
                            call_logger.error(f"OpenAI error: {error_info}")
                        else:
                            logger.error(f"OpenAI error: {error_info}")
                    
                    # Session updated
                    elif event_type == "session.updated":
                        if call_logger:
                            call_logger.debug("Session configuration updated")
            
            except asyncio.CancelledError:
                if call_logger:
                    call_logger.info("OpenAI stream cancelled")
                raise
            
            except Exception as e:
                if call_logger:
                    call_logger.error(f"Error in openai_to_twilio: {e}")
                    call_logger.error(traceback.format_exc())
                else:
                    logger.error(f"Error in openai_to_twilio: {e}")
        
        # Run both streams concurrently
        await asyncio.gather(
            twilio_to_openai(),
            openai_to_twilio(),
            return_exceptions=True
        )
    
    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
        logger.error(traceback.format_exc())
    
    finally:
        # Cleanup
        if call_sid:
            await cleanup_session(call_sid)
        
        if openai_ws:
            await openai_service.close_session(session_id)
        
        logger.info(f"WebSocket connection closed: {call_sid}")


async def execute_tool(function_name: str, arguments: dict, call_sid: str) -> dict:
    """
    Execute tool/function calls from OpenAI
    
    Args:
        function_name: Name of function to execute
        arguments: Function arguments
        call_sid: Call identifier
        
    Returns:
        Function execution result
    """
    call_logger = get_call_logger(call_sid)
    call_logger.info(f"Executing tool: {function_name} with args: {arguments}")
    
    try:
        if function_name == "lookup_order":
            # Fetch order details
            order_id = arguments.get("order_id")
            result = await db_service.get_order_details(order_id)
            
            call_logger.info(f"Order lookup result: {result.get('status', 'unknown')}")
            return result
        
        elif function_name == "transfer_to_human":
            # Transfer to human agent
            reason = arguments.get("reason")
            context = arguments.get("customer_context")
            priority = arguments.get("priority", "medium")
            
            call_logger.info(f"Transfer request - Reason: {reason}, Priority: {priority}")
            
            # Create transfer request
            transfer_result = await db_service.create_transfer_request(
                call_sid, reason, context, priority
            )
            
            # In production, trigger actual transfer workflow here
            # For now, return confirmation
            return {
                "status": "transfer_initiated",
                "message": "Bilkul, main aapko ek moment mein humare team member se connect kar deta hoon.",
                "ticket_id": transfer_result.get("ticket_id"),
                "estimated_wait_time": "2-3 minutes"
            }
        
        elif function_name == "check_product_availability":
            # Check product availability
            product_name = arguments.get("product_name")
            pincode = arguments.get("pincode")
            
            call_logger.info(f"Checking availability: {product_name}, pincode: {pincode}")
            
            availability = await db_service.check_inventory(product_name, pincode)
            return availability
        
        elif function_name == "create_ticket":
            # Create support ticket
            issue_type = arguments.get("issue_type")
            description = arguments.get("description")
            customer_phone = arguments.get("customer_phone")
            priority = arguments.get("priority", "medium")
            
            call_logger.info(f"Creating ticket: {issue_type}")
            
            ticket = await db_service.create_support_ticket(
                call_sid=call_sid,
                issue_type=issue_type,
                description=description,
                customer_phone=customer_phone,
                priority=priority
            )
            
            return {
                "status": "ticket_created",
                "ticket_id": ticket.get("ticket_id"),
                "message": f"Maine aapke liye ticket create kar diya hai. Aapka ticket number hai {ticket.get('ticket_id')}. Humari team 24 hours mein aapse contact karegi."
            }
        
        else:
            call_logger.warning(f"Unknown function: {function_name}")
            return {
                "error": f"Unknown function: {function_name}",
                "message": "I'm sorry, I couldn't process that request."
            }
    
    except Exception as e:
        call_logger.error(f"Tool execution error: {e}")
        call_logger.error(traceback.format_exc())
        
        return {
            "error": str(e),
            "message": "I encountered an error while processing your request. Let me try another way to help you."
        }


async def cleanup_session(call_sid: str):
    """
    Cleanup session resources
    
    Args:
        call_sid: Call identifier
    """
    try:
        if call_sid in active_sessions:
            session_data = active_sessions[call_sid]
            
            # Calculate metrics
            start_time = session_data.get("start_time")
            if start_time:
                duration = (datetime.utcnow() - start_time).total_seconds()
                cost_estimate = estimate_call_cost(duration)
                
                logger.info(f"Call {call_sid} completed - Duration: {duration:.1f}s, Cost: ${cost_estimate['total_cost_usd']:.4f}")
            
            # Remove from active sessions
            del active_sessions[call_sid]
            
            logger.info(f"Session cleaned up: {call_sid}")
    
    except Exception as e:
        logger.error(f"Error cleaning up session {call_sid}: {e}")


@app.post("/outbound-call")
async def initiate_outbound_call(request: OutboundCallRequest):
    """
    Initiate an outbound call
    
    Args:
        request: Outbound call request
        
    Returns:
        Call initiation status
    """
    try:
        logger.info(f"Initiating outbound call to {request.to_number}")
        
        # Sanitize phone number
        to_number = sanitize_phone_number(request.to_number)
        
        # Generate webhook URL
        webhook_url = f"https://{settings.SERVER_URL}/incoming-call"
        
        # Initiate call via Twilio
        result = await twilio_service.initiate_outbound_call(
            to_number=to_number,
            webhook_url=webhook_url,
            context=request.context
        )
        
        logger.info(f"Outbound call initiated: {result['call_sid']}")
        
        return {
            "status": "success",
            "call_sid": result["call_sid"],
            "to_number": to_number,
            "message": "Outbound call initiated successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to initiate outbound call: {e}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/call/{call_sid}")
async def get_call_details(call_sid: str):
    """
    Get details of a specific call
    
    Args:
        call_sid: Call identifier
        
    Returns:
        Call details
    """
    try:
        # Get from database
        call_record = await db_service.get_call_record(call_sid)
        
        if not call_record:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Get conversation history
        conversation = await db_service.get_conversation_history(call_sid)
        
        return {
            "call": call_record,
            "conversation": conversation,
            "is_active": call_sid in active_sessions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting call details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    try:
        active_calls = await db_service.get_active_calls_count()
        
        return {
            "active_calls": active_calls,
            "active_sessions": len(active_sessions),
            "openai_sessions": openai_service.active_session_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/call-status")
async def call_status_callback(request: Request):
    """
    Twilio status callback for call events
    
    Args:
        request: Request with status data
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        
        logger.info(f"Call status update: {call_sid} - {call_status}")
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"Error processing status callback: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
