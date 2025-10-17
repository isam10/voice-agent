"""
Helper Utilities
Various helper functions for the application
"""

import re
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import base64


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize and format phone number
    
    Args:
        phone: Raw phone number
        
    Returns:
        Sanitized phone number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Add country code if missing (assuming India +91)
    if not digits.startswith('91') and len(digits) == 10:
        digits = '91' + digits
    
    return '+' + digits


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_indian_phone(phone: str) -> bool:
    """
    Validate Indian phone number
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid Indian number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Should be 10 digits or 12 digits with country code
    if len(digits) == 10:
        return digits[0] in ['6', '7', '8', '9']
    elif len(digits) == 12:
        return digits.startswith('91') and digits[2] in ['6', '7', '8', '9']
    
    return False


def generate_session_id(prefix: str = "sess") -> str:
    """
    Generate unique session ID
    
    Args:
        prefix: ID prefix
        
    Returns:
        Unique session ID
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(4)
    return f"{prefix}_{timestamp}_{random_part}"


def generate_ticket_id(ticket_type: str = "TKT") -> str:
    """
    Generate unique ticket ID
    
    Args:
        ticket_type: Type prefix (TKT, SUP, TXF, etc.)
        
    Returns:
        Unique ticket ID
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(2).upper()
    return f"{ticket_type}-{timestamp}-{random_part}"


def calculate_duration(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    """
    Calculate duration in seconds
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp (defaults to now)
        
    Returns:
        Duration in seconds
    """
    if end_time is None:
        end_time = datetime.utcnow()
    
    delta = end_time - start_time
    return delta.total_seconds()


def format_duration(seconds: float) -> str:
    """
    Format duration as human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration (e.g., "2m 30s")
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def parse_hinglish_input(text: str) -> Dict[str, Any]:
    """
    Parse Hinglish text to extract structured information
    
    Args:
        text: Hinglish text input
        
    Returns:
        Extracted information
    """
    result = {
        "order_ids": [],
        "phone_numbers": [],
        "emails": [],
        "pincodes": []
    }
    
    # Extract order IDs (various formats)
    order_patterns = [
        r'\b[A-Z]{2,}\d{4,}\b',  # ABC1234
        r'\b\d{6,}\b',            # 123456
        r'\border[_\s-]?id[:\s]*([A-Za-z0-9]+)\b'  # order id: ABC123
    ]
    
    for pattern in order_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        result["order_ids"].extend(matches)
    
    # Extract phone numbers
    phone_pattern = r'\b(?:\+91)?[6-9]\d{9}\b'
    result["phone_numbers"] = re.findall(phone_pattern, text)
    
    # Extract emails
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    result["emails"] = re.findall(email_pattern, text)
    
    # Extract pincodes
    pincode_pattern = r'\b[1-9]\d{5}\b'
    result["pincodes"] = re.findall(pincode_pattern, text)
    
    return result


def detect_language(text: str) -> str:
    """
    Detect language/script from text
    
    Args:
        text: Input text
        
    Returns:
        Language code (en, hi, hinglish)
    """
    # Check for Devanagari script (Hindi)
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
    
    # Check for English
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    total_chars = len(text.strip())
    
    if total_chars == 0:
        return "unknown"
    
    hindi_ratio = hindi_chars / total_chars
    
    if hindi_ratio > 0.7:
        return "hi"
    elif hindi_ratio > 0.1 and english_words > 0:
        return "hinglish"
    else:
        return "en"


def mask_sensitive_data(data: str, data_type: str = "phone") -> str:
    """
    Mask sensitive data for logging
    
    Args:
        data: Sensitive data to mask
        data_type: Type of data (phone, email, card)
        
    Returns:
        Masked data
    """
    if data_type == "phone":
        # Show last 4 digits only
        if len(data) > 4:
            return "*" * (len(data) - 4) + data[-4:]
        return "****"
    
    elif data_type == "email":
        # Mask username part
        if '@' in data:
            username, domain = data.split('@', 1)
            masked_username = username[0] + "*" * (len(username) - 1)
            return f"{masked_username}@{domain}"
        return "***@***.com"
    
    elif data_type == "card":
        # Show last 4 digits only
        digits = re.sub(r'\D', '', data)
        if len(digits) > 4:
            return "*" * (len(digits) - 4) + digits[-4:]
        return "****"
    
    return "****"


def hash_identifier(identifier: str, salt: Optional[str] = None) -> str:
    """
    Create hash of identifier for privacy
    
    Args:
        identifier: Original identifier
        salt: Optional salt for hashing
        
    Returns:
        Hashed identifier
    """
    if salt is None:
        salt = "voice_agent_default_salt"
    
    combined = f"{identifier}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def estimate_call_cost(duration_seconds: float) -> Dict[str, float]:
    """
    Estimate cost of call
    
    Args:
        duration_seconds: Call duration in seconds
        
    Returns:
        Cost breakdown
    """
    duration_minutes = duration_seconds / 60
    
    # Cost estimates (adjust based on actual rates)
    openai_cost_per_min = 0.24  # $0.24 per minute
    twilio_cost_per_min = 0.01  # $0.01 per minute
    
    openai_cost = duration_minutes * openai_cost_per_min
    twilio_cost = duration_minutes * twilio_cost_per_min
    total_cost = openai_cost + twilio_cost
    
    return {
        "duration_minutes": round(duration_minutes, 2),
        "openai_cost_usd": round(openai_cost, 4),
        "twilio_cost_usd": round(twilio_cost, 4),
        "total_cost_usd": round(total_cost, 4),
        "total_cost_inr": round(total_cost * 83, 2)  # Approx USD to INR
    }


def is_business_hours(
    current_time: Optional[datetime] = None,
    start_hour: int = 9,
    end_hour: int = 18
) -> bool:
    """
    Check if current time is within business hours
    
    Args:
        current_time: Time to check (defaults to now)
        start_hour: Business start hour
        end_hour: Business end hour
        
    Returns:
        True if within business hours
    """
    if current_time is None:
        current_time = datetime.now()
    
    current_hour = current_time.hour
    return start_hour <= current_hour < end_hour


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
    """
    import functools
    import asyncio
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
            
        return wrapper
    return decorator
