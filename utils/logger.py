"""
Logging Configuration
Sets up structured logging for the application
"""

import logging
import sys
from datetime import datetime
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "call_sid"):
            log_data["call_sid"] = record.call_sid
        
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        
        return json.dumps(log_data)


def setup_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    use_json: bool = False
) -> logging.Logger:
    """
    Set up and configure logger
    
    Args:
        name: Logger name (defaults to root logger)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or "voice_agent")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance
    
    Args:
        name: Logger name
        level: Optional log level override
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Logger hasn't been set up yet
        from config.settings import settings
        log_level = level or settings.LOG_LEVEL
        return setup_logger(name, log_level)
    
    return logger


class CallLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds call context to all log messages"""
    
    def __init__(self, logger: logging.Logger, call_sid: str):
        super().__init__(logger, {"call_sid": call_sid})
    
    def process(self, msg, kwargs):
        # Add call_sid to extra fields
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["call_sid"] = self.extra["call_sid"]
        return msg, kwargs


def get_call_logger(call_sid: str, base_logger: Optional[logging.Logger] = None) -> CallLoggerAdapter:
    """
    Get a logger adapter with call context
    
    Args:
        call_sid: Call SID for context
        base_logger: Base logger to wrap (defaults to voice_agent logger)
        
    Returns:
        Logger adapter with call context
    """
    if base_logger is None:
        base_logger = get_logger("voice_agent")
    
    return CallLoggerAdapter(base_logger, call_sid)
