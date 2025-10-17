"""
Twilio Service
Handles Twilio-specific operations like outbound calls, call management
"""

from typing import Optional, Dict
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from utils.logger import get_logger

logger = get_logger(__name__)


class TwilioService:
    """Service for Twilio operations"""
    
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        self.client = Client(account_sid, auth_token)
        self.phone_number = phone_number
        self.account_sid = account_sid
    
    def generate_connect_twiml(self, stream_url: str, call_sid: str, from_number: str) -> str:
        """
        Generate TwiML to connect call to WebSocket stream
        
        Args:
            stream_url: WebSocket URL to connect to
            call_sid: Twilio Call SID
            from_number: Caller's phone number
            
        Returns:
            TwiML XML string
        """
        try:
            response = VoiceResponse()
            connect = Connect()
            stream = Stream(url=stream_url)
            
            # Add parameters
            stream.parameter(name='callSid', value=call_sid)
            stream.parameter(name='from', value=from_number)
            
            connect.append(stream)
            response.append(connect)
            
            twiml = str(response)
            logger.debug(f"Generated TwiML for call {call_sid}")
            
            return twiml
            
        except Exception as e:
            logger.error(f"Failed to generate TwiML: {e}")
            raise
    
    async def initiate_outbound_call(
        self,
        to_number: str,
        webhook_url: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Initiate an outbound call
        
        Args:
            to_number: Phone number to call
            webhook_url: URL for call handling
            context: Optional context data
            
        Returns:
            Call details
        """
        try:
            logger.info(f"Initiating outbound call to {to_number}")
            
            # Create status callback URL with context if provided
            status_callback = f"{webhook_url}/call-status"
            
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=webhook_url,
                status_callback=status_callback,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                method='POST'
            )
            
            logger.info(f"Outbound call created: {call.sid}")
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "to": to_number,
                "from": self.phone_number
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate outbound call: {e}")
            raise
    
    async def update_call_status(self, call_sid: str, status: str):
        """
        Update call status (e.g., cancel, complete)
        
        Args:
            call_sid: Twilio Call SID
            status: New status
        """
        try:
            call = self.client.calls(call_sid).update(status=status)
            logger.info(f"Call {call_sid} updated to status: {status}")
            
            return {
                "call_sid": call_sid,
                "status": call.status
            }
            
        except Exception as e:
            logger.error(f"Failed to update call status: {e}")
            raise
    
    async def get_call_details(self, call_sid: str) -> Dict:
        """
        Get details of a call
        
        Args:
            call_sid: Twilio Call SID
            
        Returns:
            Call details
        """
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "call_sid": call.sid,
                "from": call.from_formatted,
                "to": call.to_formatted,
                "status": call.status,
                "duration": call.duration,
                "start_time": str(call.start_time) if call.start_time else None,
                "end_time": str(call.end_time) if call.end_time else None,
                "price": call.price,
                "direction": call.direction
            }
            
        except Exception as e:
            logger.error(f"Failed to get call details: {e}")
            raise
    
    async def transfer_call(self, call_sid: str, transfer_url: str) -> Dict:
        """
        Transfer call to another URL (e.g., human agent)
        
        Args:
            call_sid: Twilio Call SID
            transfer_url: URL to transfer to
            
        Returns:
            Transfer status
        """
        try:
            logger.info(f"Transferring call {call_sid} to {transfer_url}")
            
            call = self.client.calls(call_sid).update(
                url=transfer_url,
                method='POST'
            )
            
            return {
                "call_sid": call_sid,
                "status": "transferred",
                "new_url": transfer_url
            }
            
        except Exception as e:
            logger.error(f"Failed to transfer call: {e}")
            raise
    
    def validate_webhook_signature(
        self,
        url: str,
        params: Dict,
        signature: str
    ) -> bool:
        """
        Validate Twilio webhook signature for security
        
        Args:
            url: Full webhook URL
            params: POST parameters
            signature: X-Twilio-Signature header
            
        Returns:
            True if valid, False otherwise
        """
        from twilio.request_validator import RequestValidator
        
        try:
            validator = RequestValidator(self.client.auth[1])
            return validator.validate(url, params, signature)
            
        except Exception as e:
            logger.error(f"Signature validation error: {e}")
            return False
    
    async def send_sms(self, to_number: str, message: str) -> Dict:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number
            message: Message text
            
        Returns:
            Message details
        """
        try:
            message = self.client.messages.create(
                to=to_number,
                from_=self.phone_number,
                body=message
            )
            
            logger.info(f"SMS sent to {to_number}: {message.sid}")
            
            return {
                "message_sid": message.sid,
                "status": message.status,
                "to": to_number
            }
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            raise
