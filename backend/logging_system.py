import enum
import inspect
import datetime
from typing import Optional
from fastapi import Request
from config.settings import get_settings

class PriorityLevel(enum.Enum):
    """Logging priority levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

def logger(priority_level: PriorityLevel, message: str, user_id: Optional[str] = None, module: Optional[str] = None) -> None:
    """
    Centralized logging function for the backend.
    
    Args:
        priority_level: One of DEBUG, INFO, WARNING, ERROR, or CRITICAL
        message: The fully formatted string to print
        user_id: Optional user ID override. If None, attempts to auto-detect from request context
        module: Optional module name override. If None, attempts to auto-detect from call stack
    """
    # Get logging priority level from settings
    try:
        settings = get_settings()
        configured_level = settings.logging_priority_level.upper()
    except Exception:
        configured_level = "INFO"  # Default fallback
    
    # Check if this message should be logged based on priority level
    priority_order = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4
    }
    
    if priority_order.get(priority_level.value, 0) < priority_order.get(configured_level, 1):
        return  # Skip logging this message
    
    # Get timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Auto-detect module if not provided
    if module is None:
        try:
            # Get the calling frame (skip this function and its caller)
            frame = inspect.currentframe()
            if frame:
                # Go up 2 levels: 1 for this function, 1 for the caller
                caller_frame = frame.f_back
                if caller_frame:
                    caller_frame = caller_frame.f_back
                    if caller_frame:
                        module_name = inspect.getmodule(caller_frame)
                        if module_name:
                            module = module_name.__name__
                        else:
                            module = "undetermined"
                    else:
                        module = "undetermined"
                else:
                    module = "undetermined"
            else:
                module = "undetermined"
        except Exception:
            module = "undetermined"
    
    # Auto-detect user_id if not provided
    if user_id is None:
        try:
            # Try to get user_id from the current request context
            # This is a simplified approach - in practice, you might need to pass the request object
            # or use a more sophisticated context management system
            user_id = "none"
        except Exception:
            user_id = "none"
    
    # Format and print the log message
    log_entry = f"{timestamp}, {priority_level.value}, {message}, {user_id}, {module}"
    print(log_entry)

# Convenience functions for each priority level
def debug(message: str, user_id: Optional[str] = None, module: Optional[str] = None) -> None:
    """Log a DEBUG level message"""
    logger(PriorityLevel.DEBUG, message, user_id, module)

def info(message: str, user_id: Optional[str] = None, module: Optional[str] = None) -> None:
    """Log an INFO level message"""
    logger(PriorityLevel.INFO, message, user_id, module)

def warning(message: str, user_id: Optional[str] = None, module: Optional[str] = None) -> None:
    """Log a WARNING level message"""
    logger(PriorityLevel.WARNING, message, user_id, module)

def error(message: str, user_id: Optional[str] = None, module: Optional[str] = None) -> None:
    """Log an ERROR level message"""
    logger(PriorityLevel.ERROR, message, user_id, module)

def critical(message: str, user_id: Optional[str] = None, module: Optional[str] = None) -> None:
    """Log a CRITICAL level message"""
    logger(PriorityLevel.CRITICAL, message, user_id, module)
