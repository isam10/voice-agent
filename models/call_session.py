"""
Call Session Models
Data models for call sessions and related entities
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CallStatus(str, Enum):
    """Call status enumeration"""
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELLED = "cancelled"


class CallDirection(str, Enum):
    """Call direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CallSession(BaseModel):
    """Call session data model"""
    
    call_sid: str = Field(..., description="Twilio Call SID")
    stream_sid: Optional[str] = Field(None, description="Twilio Stream SID")
    direction: CallDirection = Field(CallDirection.INBOUND, description="Call direction")
    from_number: str = Field(..., description="Caller's phone number")
    to_number: str = Field(..., description="Recipient's phone number")
    status: CallStatus = Field(CallStatus.INITIATED, description="Current call status")
    
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Call start time")
    end_time: Optional[datetime] = Field(None, description="Call end time")
    duration: Optional[float] = Field(None, description="Call duration in seconds")
    
    openai_session_id: Optional[str] = Field(None, description="OpenAI session identifier")
    
    customer_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Customer-specific context data"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    class Config:
        use_enum_values = True


class ConversationItem(BaseModel):
    """Conversation turn/item"""
    
    call_sid: str
    item_id: str
    item_type: str  # message, function_call, function_call_output
    role: Optional[str] = None  # user, assistant, system
    content: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FunctionCall(BaseModel):
    """Function call details"""
    
    call_id: str
    function_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TransferRequest(BaseModel):
    """Transfer to human agent request"""
    
    ticket_id: str
    call_sid: str
    reason: str
    customer_context: str
    priority: Priority = Priority.MEDIUM
    status: str = "queued"  # queued, assigned, completed
    assigned_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SupportTicket(BaseModel):
    """Support ticket"""
    
    ticket_id: str
    call_sid: str
    issue_type: str
    description: str
    customer_phone: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: str = "open"  # open, in-progress, resolved, closed
    assigned_agent: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class OrderDetails(BaseModel):
    """Order details model"""
    
    order_id: str
    status: str
    order_date: str
    delivery_date: Optional[str] = None
    items: List[Dict[str, Any]] = Field(default_factory=list)
    subtotal: str
    shipping: str
    total: str
    payment_method: Optional[str] = None
    shipping_address: Optional[str] = None


class ProductAvailability(BaseModel):
    """Product availability model"""
    
    product: str
    available: bool
    stock_count: Optional[int] = None
    delivery_estimate: Optional[str] = None
    price: Optional[str] = None
    pincode_serviceable: Optional[bool] = None


class OutboundCallRequest(BaseModel):
    """Request to initiate outbound call"""
    
    to_number: str = Field(..., description="Phone number to call")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Context data for the call"
    )
    priority: Priority = Priority.MEDIUM
    scheduled_time: Optional[datetime] = None


class CallMetrics(BaseModel):
    """Call metrics and analytics"""
    
    total_calls: int = 0
    active_calls: int = 0
    completed_calls: int = 0
    failed_calls: int = 0
    average_duration: float = 0.0
    total_duration: float = 0.0
    transfer_rate: float = 0.0
    success_rate: float = 0.0
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
