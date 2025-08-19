# Database module initialization

from database.database import (
    init_db, 
    get_user, 
    create_user, 
    update_user,
    update_user_field,
    update_user_login,
    update_user_password,
    update_user_role,
    get_user_preferences, 
    save_user_preference,
    get_user_settings,
    save_user_settings,
    log_api_call,
    log_error,
    update_user_activity_summary
)

from database.analytics_functions import (
    get_analytics_overview,
    get_daily_usage,
    get_model_usage,
    get_feature_usage,
    get_error_distribution
)

# Ensure these are available at the module level
__all__ = [
    'init_db',
    'get_user',
    'create_user',
    'update_user',
    'update_user_field',
    'update_user_login',
    'update_user_password',
    'update_user_role',
    'get_user_preferences',
    'save_user_preference',
    'get_user_settings',
    'save_user_settings',
    'log_api_call',
    'log_error',
    'update_user_activity_summary',
    'get_analytics_overview',
    'get_daily_usage',
    'get_model_usage',
    'get_feature_usage',
    'get_error_distribution'
]
