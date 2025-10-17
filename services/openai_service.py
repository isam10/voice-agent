"""
OpenAI Realtime API Service
Handles connection and communication with OpenAI's realtime API
"""

import asyncio
import json
from typing import Optional, Dict, Any, Callable
from openai import AsyncOpenAI
from config.agent_config import AGENT_CONFIG, AUDIO_CONFIG
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for managing OpenAI Realtime API connections"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.active_connections: Dict[str, Any] = {}
    
    async def create_session(self, session_id: str) -> Any:
        """
        Create a new OpenAI Realtime API session
        
        Args:
            session_id: Unique identifier for this session
            
        Returns:
            OpenAI WebSocket connection
        """
        try:
            logger.info(f"Creating OpenAI session: {session_id}")
            
            connection = await self.client.beta.realtime.connect(
                model=AGENT_CONFIG["model"]
            )
            
            self.active_connections[session_id] = connection
            
            # Configure the session
            await self.configure_session(connection)
            
            logger.info(f"OpenAI session created successfully: {session_id}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create OpenAI session {session_id}: {e}")
            raise
    
    async def configure_session(self, connection: Any):
        """
        Configure OpenAI session with agent settings
        
        Args:
            connection: OpenAI WebSocket connection
        """
        try:
            config = {
                "type": "session.update",
                "session": {
                    "instructions": AGENT_CONFIG["instructions"],
                    "voice": AGENT_CONFIG["voice"],
                    "temperature": AGENT_CONFIG["temperature"],
                    "tools": AGENT_CONFIG["tools"],
                    "tool_choice": "auto",
                    "input_audio_format": AUDIO_CONFIG["input_format"],
                    "output_audio_format": AUDIO_CONFIG["output_format"],
                    "turn_detection": AGENT_CONFIG["turn_detection"],
                    "max_response_output_tokens": AGENT_CONFIG["max_response_output_tokens"]
                }
            }
            
            await connection.send(config)
            logger.debug("Session configuration sent")
            
        except Exception as e:
            logger.error(f"Failed to configure session: {e}")
            raise
    
    async def send_initial_greeting(self, connection: Any):
        """
        Send initial greeting to start conversation
        
        Args:
            connection: OpenAI WebSocket connection
        """
        try:
            await connection.send({
                "type": "response.create",
                "response": {
                    "modalities": ["audio"],
                    "instructions": "Greet the customer warmly in Hinglish and ask how you can help them today."
                }
            })
            logger.debug("Initial greeting sent")
            
        except Exception as e:
            logger.error(f"Failed to send greeting: {e}")
            raise
    
    async def send_audio(self, connection: Any, audio_data: str):
        """
        Send audio data to OpenAI
        
        Args:
            connection: OpenAI WebSocket connection
            audio_data: Base64 encoded audio data
        """
        try:
            await connection.send({
                "type": "input_audio_buffer.append",
                "audio": audio_data
            })
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            raise
    
    async def send_function_result(
        self,
        connection: Any,
        call_id: str,
        result: Dict[str, Any]
    ):
        """
        Send function execution result back to OpenAI
        
        Args:
            connection: OpenAI WebSocket connection
            call_id: Function call ID
            result: Function execution result
        """
        try:
            await connection.send({
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            })
            
            # Trigger response generation
            await connection.send({"type": "response.create"})
            
            logger.debug(f"Function result sent for call_id: {call_id}")
            
        except Exception as e:
            logger.error(f"Failed to send function result: {e}")
            raise
    
    async def close_session(self, session_id: str):
        """
        Close OpenAI session and cleanup
        
        Args:
            session_id: Session identifier
        """
        try:
            if session_id in self.active_connections:
                connection = self.active_connections[session_id]
                
                # Close the connection
                if hasattr(connection, 'close'):
                    await connection.close()
                
                # Remove from active connections
                del self.active_connections[session_id]
                
                logger.info(f"OpenAI session closed: {session_id}")
                
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")
    
    async def handle_event_stream(
        self,
        connection: Any,
        event_handler: Callable
    ):
        """
        Handle incoming events from OpenAI
        
        Args:
            connection: OpenAI WebSocket connection
            event_handler: Async callback function to handle events
        """
        try:
            async for event in connection:
                try:
                    await event_handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Event stream cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in event stream: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Any]:
        """
        Get active session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            OpenAI connection or None
        """
        return self.active_connections.get(session_id)
    
    @property
    def active_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_connections)
