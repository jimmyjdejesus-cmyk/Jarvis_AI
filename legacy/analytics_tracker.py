import time
import json
import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
import database

logger = logging.getLogger(__name__)


def track_api_call(endpoint_type: str, model_name: str = None):
    """Decorator to track API calls with analytics"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user and session info
            username = kwargs.get('user') or kwargs.get('username') or 'anonymous'
            session_id = kwargs.get('session_id')
            
            # Start timing
            start_time = time.time()
            prompt_tokens = 0
            response_tokens = 0
            success = True
            error_type = None
            error_message = None
            
            try:
                # Extract prompt for token counting (approximate)
                prompt = kwargs.get('prompt') or (args[0] if args else '')
                if prompt:
                    prompt_tokens = estimate_tokens(str(prompt))
                
                # Call the actual function
                result = func(*args, **kwargs)
                
                # Estimate response tokens
                if result:
                    response_tokens = estimate_tokens(str(result))
                
                return result
                
            except Exception as e:
                success = False
                error_type = type(e).__name__
                error_message = str(e)
                
                # Log the error for analytics
                database.log_error(
                    username=username,
                    session_id=session_id,
                    error_type=error_type,
                    error_message=error_message,
                    stack_trace=traceback.format_exc(),
                    context={
                        'endpoint_type': endpoint_type,
                        'model_name': model_name,
                        'function': func.__name__
                    }
                )
                
                raise  # Re-raise the exception
                
            finally:
                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Log the API call
                database.log_api_call(
                    username=username,
                    session_id=session_id,
                    endpoint_type=endpoint_type,
                    model_name=model_name,
                    prompt_tokens=prompt_tokens,
                    response_tokens=response_tokens,
                    latency_ms=latency_ms,
                    success=success,
                    error_type=error_type,
                    error_message=error_message
                )
                
                # Update user activity summary
                from datetime import datetime
                today = datetime.now().date().isoformat()
                database.update_user_activity_summary(username, today)
        
        return wrapper
    return decorator


def track_feature_usage(feature_name: str, action: str = "used"):
    """Decorator to track feature usage"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get user and session info
            username = getattr(args[0] if args else None, 'username', None) or 'anonymous'
            session_id = getattr(args[0] if args else None, 'session_id', None)
            
            try:
                # Call the actual function
                result = func(*args, **kwargs)
                
                # Log feature usage
                database.log_feature_usage(
                    username=username,
                    feature_name=feature_name,
                    action=action,
                    metadata={
                        'function': func.__name__,
                        'success': True
                    },
                    session_id=session_id
                )
                
                return result
                
            except Exception as e:
                # Log feature usage failure
                database.log_feature_usage(
                    username=username,
                    feature_name=feature_name,
                    action=f"{action}_failed",
                    metadata={
                        'function': func.__name__,
                        'error': str(e),
                        'success': False
                    },
                    session_id=session_id
                )
                
                raise  # Re-raise the exception
        
        return wrapper
    return decorator


def estimate_tokens(text: str) -> int:
    """Estimate token count for text (rough approximation)"""
    if not text:
        return 0
    
    # Simple approximation: 1 token ≈ 4 characters for English text
    # This is very rough but better than nothing
    return max(1, len(text) // 4)


def log_chat_interaction(username: str, session_id: int, user_message: str, 
                        ai_response: str, model_name: str = None, 
                        latency_ms: int = None, sources: list = None):
    """Log a complete chat interaction with analytics"""
    
    # Log the API call
    database.log_api_call(
        username=username,
        session_id=session_id,
        endpoint_type='chat',
        model_name=model_name,
        prompt_tokens=estimate_tokens(user_message),
        response_tokens=estimate_tokens(ai_response),
        latency_ms=latency_ms,
        success=True
    )
    
    # Log feature usage
    database.log_feature_usage(
        username=username,
        feature_name='chat',
        action='message_sent',
        metadata={
            'has_sources': bool(sources),
            'source_count': len(sources) if sources else 0,
            'model': model_name
        },
        session_id=session_id
    )


def log_rag_usage(username: str, session_id: int, query: str, 
                 sources_found: int, model_name: str = None,
                 latency_ms: int = None, success: bool = True):
    """Log RAG feature usage"""
    
    # Log the API call
    database.log_api_call(
        username=username,
        session_id=session_id,
        endpoint_type='rag',
        model_name=model_name,
        prompt_tokens=estimate_tokens(query),
        response_tokens=0,  # RAG doesn't generate tokens, just finds sources
        latency_ms=latency_ms,
        success=success
    )
    
    # Log feature usage
    database.log_feature_usage(
        username=username,
        feature_name='rag',
        action='search_performed',
        metadata={
            'sources_found': sources_found,
            'model': model_name,
            'success': success
        },
        session_id=session_id
    )


def log_file_operation(username: str, operation: str, file_count: int = 1,
                      file_types: list = None, success: bool = True,
                      error_message: str = None):
    """Log file operations (upload, download, etc.)"""
    
    # Log feature usage
    database.log_feature_usage(
        username=username,
        feature_name='file_operations',
        action=operation,
        metadata={
            'file_count': file_count,
            'file_types': file_types or [],
            'success': success,
            'error': error_message
        }
    )
    
    # Log error if operation failed
    if not success and error_message:
        database.log_error(
            username=username,
            error_type='file_operation_error',
            error_message=error_message,
            context={
                'operation': operation,
                'file_count': file_count,
                'file_types': file_types
            }
        )


def log_model_selection(username: str, expert_model: str = None, 
                       draft_model: str = None, session_id: int = None):
    """Log model selection changes"""
    
    database.log_feature_usage(
        username=username,
        feature_name='model_selection',
        action='model_changed',
        metadata={
            'expert_model': expert_model,
            'draft_model': draft_model
        },
        session_id=session_id
    )


def log_settings_change(username: str, setting_name: str, old_value: Any = None,
                       new_value: Any = None):
    """Log user settings changes"""
    
    database.log_feature_usage(
        username=username,
        feature_name='settings',
        action='setting_changed',
        metadata={
            'setting_name': setting_name,
            'old_value': old_value,
            'new_value': new_value
        }
    )


def log_session_activity(username: str, action: str, session_id: int = None,
                        project_name: str = None):
    """Log session-related activities"""
    
    database.log_feature_usage(
        username=username,
        feature_name='session_management',
        action=action,
        metadata={
            'project_name': project_name
        },
        session_id=session_id
    )


def log_admin_action(admin_username: str, action: str, target_user: str = None,
                    details: Dict = None):
    """Log admin actions for audit trail"""
    
    database.log_feature_usage(
        username=admin_username,
        feature_name='admin_panel',
        action=action,
        metadata={
            'target_user': target_user,
            'details': details or {}
        }
    )
    
    # Also log as security event
    database.log_security_event(
        event_type=f"ADMIN_{action.upper()}",
        username=admin_username,
        details=f"Action: {action}, Target: {target_user}, Details: {json.dumps(details or {})}"
    )


class AnalyticsContext:
    """Context manager for tracking complex operations"""
    
    def __init__(self, username: str, operation: str, session_id: int = None):
        self.username = username
        self.operation = operation
        self.session_id = session_id
        self.start_time = None
        self.metadata = {}
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        latency_ms = int((time.time() - self.start_time) * 1000)
        
        self.metadata.update({
            'latency_ms': latency_ms,
            'success': success
        })
        
        if exc_type:
            self.metadata.update({
                'error_type': exc_type.__name__,
                'error_message': str(exc_val)
            })
            
            # Log error
            database.log_error(
                username=self.username,
                session_id=self.session_id,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                stack_trace=traceback.format_exc(),
                context={
                    'operation': self.operation,
                    'metadata': self.metadata
                }
            )
        
        # Log the operation
        database.log_feature_usage(
            username=self.username,
            feature_name=self.operation,
            action='completed' if success else 'failed',
            metadata=self.metadata,
            session_id=self.session_id
        )
    
    def add_metadata(self, **kwargs):
        """Add metadata to the analytics context"""
        self.metadata.update(kwargs)


# Helper functions for common tracking scenarios

def track_login_attempt(username: str, success: bool, ip_address: str = None,
                       user_agent: str = None, error_message: str = None):
    """Track login attempts"""
    event_type = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
    
    database.log_security_event(
        event_type=event_type,
        username=username,
        ip_address=ip_address,
        user_agent=user_agent,
        details=error_message if error_message else None
    )
    
    if not success:
        database.log_error(
            username=username,
            error_type='authentication_error',
            error_message=error_message or 'Login failed',
            context={
                'ip_address': ip_address,
                'user_agent': user_agent
            }
        )


def track_performance_metrics(username: str, session_id: int, latency: float,
                             operation: str = 'general'):
    """Track performance metrics"""
    database.log_feature_usage(
        username=username,
        feature_name='performance',
        action='metric_recorded',
        metadata={
            'operation': operation,
            'latency_seconds': latency,
            'latency_ms': int(latency * 1000)
        },
        session_id=session_id
    )