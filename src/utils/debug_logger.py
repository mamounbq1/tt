"""
Enhanced Logging and Error Handling Configuration
Provides comprehensive debugging and error tracking
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path


class DebugLogger:
    """Enhanced logger with multiple output streams and detailed formatting"""
    
    def __init__(self, name, log_dir='logs'):
        """
        Initialize logger with file and console handlers
        
        Args:
            name: Logger name (usually module name)
            log_dir: Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler - DEBUG (all messages)
        debug_file = self.log_dir / f'{name}_debug.log'
        debug_handler = logging.FileHandler(debug_file, mode='a', encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(debug_handler)
        
        # File handler - ERROR (errors only)
        error_file = self.log_dir / f'{name}_errors.log'
        error_handler = logging.FileHandler(error_file, mode='a', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # Daily log file
        today = datetime.now().strftime('%Y-%m-%d')
        daily_file = self.log_dir / f'{name}_{today}.log'
        daily_handler = logging.FileHandler(daily_file, mode='a', encoding='utf-8')
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(daily_handler)
    
    def debug(self, message, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, exc_info=True, **kwargs):
        """Log error message with exception info"""
        self.logger.error(message, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, message, *args, exc_info=True, **kwargs):
        """Log critical message with exception info"""
        self.logger.critical(message, *args, exc_info=exc_info, **kwargs)
    
    def log_function_entry(self, func_name, **kwargs):
        """Log function entry with parameters"""
        params = ', '.join(f'{k}={v}' for k, v in kwargs.items())
        self.debug(f"ENTER {func_name}({params})")
    
    def log_function_exit(self, func_name, result=None):
        """Log function exit with result"""
        if result is not None:
            self.debug(f"EXIT {func_name} -> {result}")
        else:
            self.debug(f"EXIT {func_name}")
    
    def log_database_operation(self, operation, table, **kwargs):
        """Log database operation"""
        params = ', '.join(f'{k}={v}' for k, v in kwargs.items())
        self.debug(f"DB {operation} on {table}: {params}")
    
    def log_exception(self, exception, context=""):
        """Log exception with context"""
        if context:
            self.error(f"Exception in {context}: {type(exception).__name__}: {str(exception)}")
        else:
            self.error(f"Exception: {type(exception).__name__}: {str(exception)}")


def setup_global_logging():
    """Setup global logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Global log file
    global_log = log_dir / 'application.log'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.FileHandler(global_log, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log startup
    logging.info("=" * 80)
    logging.info("APPLICATION STARTED")
    logging.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Working directory: {os.getcwd()}")
    logging.info("=" * 80)


def log_system_info():
    """Log system information for debugging"""
    logger = logging.getLogger(__name__)
    
    logger.info("=== SYSTEM INFORMATION ===")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Environment variables
    logger.debug("Environment variables:")
    for key, value in os.environ.items():
        if 'PATH' in key or 'PYTHON' in key:
            logger.debug(f"  {key}={value}")


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_database_error(error, operation, logger):
        """Handle database-related errors"""
        error_msg = f"Database error during {operation}: {type(error).__name__}: {str(error)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'error_type': type(error).__name__
        }
    
    @staticmethod
    def handle_file_error(error, filepath, operation, logger):
        """Handle file operation errors"""
        error_msg = f"File error during {operation} on {filepath}: {type(error).__name__}: {str(error)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'error_type': type(error).__name__,
            'filepath': str(filepath)
        }
    
    @staticmethod
    def handle_validation_error(error, context, logger):
        """Handle validation errors"""
        error_msg = f"Validation error in {context}: {str(error)}"
        logger.warning(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'error_type': 'ValidationError'
        }
    
    @staticmethod
    def handle_generic_error(error, context, logger):
        """Handle generic errors"""
        error_msg = f"Error in {context}: {type(error).__name__}: {str(error)}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'error_type': type(error).__name__
        }


# Decorator for function logging
def log_function_call(logger):
    """Decorator to log function calls with parameters and return values"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Log entry
            func_name = func.__name__
            logger.debug(f">>> ENTER {func_name}")
            logger.debug(f"    Args: {args}")
            logger.debug(f"    Kwargs: {kwargs}")
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log exit
                logger.debug(f"<<< EXIT {func_name}")
                logger.debug(f"    Result: {result}")
                
                return result
                
            except Exception as e:
                # Log exception
                logger.error(f"!!! EXCEPTION in {func_name}: {type(e).__name__}: {str(e)}")
                raise
        
        return wrapper
    return decorator


# Decorator for error handling
def handle_errors(logger, default_return=None):
    """Decorator to handle errors and return default value"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {type(e).__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator


if __name__ == '__main__':
    # Test the logger
    setup_global_logging()
    log_system_info()
    
    # Test DebugLogger
    test_logger = DebugLogger('test_module')
    test_logger.info("Test info message")
    test_logger.debug("Test debug message")
    test_logger.warning("Test warning message")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        test_logger.log_exception(e, "test context")
    
    print("\n✅ Logging system initialized successfully!")
    print(f"   Log files created in: logs/")
    print(f"   - test_module_debug.log (all messages)")
    print(f"   - test_module_errors.log (errors only)")
    print(f"   - test_module_{datetime.now().strftime('%Y-%m-%d')}.log (daily log)")
    print(f"   - application.log (global log)")
