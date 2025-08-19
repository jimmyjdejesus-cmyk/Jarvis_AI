"""
Analytics functions for the Jarvis AI database
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DB_NAME = 'janus_database.db'


def get_analytics_overview(days: int = 30) -> Dict[str, Any]:
    """
    Get analytics overview for the dashboard
    
    Args:
        days: Number of days to look back
        
    Returns:
        Dictionary with analytics overview data
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Total conversations
        cursor.execute('''
            SELECT COUNT(DISTINCT session_id) 
            FROM conversation_history 
            WHERE timestamp >= ?
        ''', (since_date,))
        total_conversations = cursor.fetchone()[0] or 0
        
        # Total messages
        cursor.execute('''
            SELECT COUNT(*) 
            FROM conversation_history 
            WHERE timestamp >= ?
        ''', (since_date,))
        total_messages = cursor.fetchone()[0] or 0
        
        # Active users
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) 
            FROM conversation_history 
            WHERE timestamp >= ?
        ''', (since_date,))
        active_users = cursor.fetchone()[0] or 0
        
        # Average response time (if tracked)
        avg_response_time = 0
        try:
            cursor.execute('''
                SELECT AVG(latency_ms)/1000.0
                FROM api_call_analytics 
                WHERE timestamp >= ? AND success = 1
            ''', (since_date,))
            result = cursor.fetchone()
            if result and result[0]:
                avg_response_time = result[0]
        except sqlite3.OperationalError:
            # Table might not exist
            pass
        
        conn.close()
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "active_users": active_users,
            "avg_response_time": avg_response_time
        }
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "active_users": 0,
            "avg_response_time": 0
        }


def get_daily_usage(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get daily usage stats for the chart
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of daily stats
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Generate date range
        date_range = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
            date_range.append(date)
        
        # Get conversation counts by day
        cursor.execute('''
            SELECT date(timestamp) as date, COUNT(DISTINCT session_id) as count
            FROM conversation_history
            WHERE timestamp >= ?
            GROUP BY date(timestamp)
        ''', (since_date,))
        conversations_by_date = dict(cursor.fetchall())
        
        # Get message counts by day
        cursor.execute('''
            SELECT date(timestamp) as date, COUNT(*) as count
            FROM conversation_history
            WHERE timestamp >= ?
            GROUP BY date(timestamp)
        ''', (since_date,))
        messages_by_date = dict(cursor.fetchall())
        
        conn.close()
        
        # Build result
        result = []
        for date in date_range:
            result.append({
                "date": date,
                "conversations": conversations_by_date.get(date, 0),
                "messages": messages_by_date.get(date, 0)
            })
        
        return result
    except Exception as e:
        logger.error(f"Failed to get daily usage: {e}")
        return []


def get_model_usage(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get model usage stats
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of model usage stats
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if the api_call_analytics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_call_analytics'")
        if not cursor.fetchone():
            # If the table doesn't exist, try using user preferences
            cursor.execute('''
                SELECT value, COUNT(*) as count
                FROM user_preferences
                WHERE key = 'model' AND value IS NOT NULL
                GROUP BY value
                ORDER BY count DESC
            ''')
            model_data = cursor.fetchall()
            
            conn.close()
            
            result = []
            for model, count in model_data:
                result.append({
                    "model": model,
                    "count": count,
                    "percentage": 0  # Calculate percentages later
                })
            
            # Calculate percentages
            total = sum(item["count"] for item in result)
            if total > 0:
                for item in result:
                    item["percentage"] = (item["count"] / total) * 100
            
            return result
        
        # If the table exists, query it
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT model_name, COUNT(*) as count
            FROM api_call_analytics
            WHERE timestamp >= ? AND model_name IS NOT NULL
            GROUP BY model_name
            ORDER BY count DESC
        ''', (since_date,))
        model_data = cursor.fetchall()
        
        conn.close()
        
        result = []
        for model, count in model_data:
            result.append({
                "model": model,
                "count": count,
                "percentage": 0  # Calculate percentages later
            })
        
        # Calculate percentages
        total = sum(item["count"] for item in result)
        if total > 0:
            for item in result:
                item["percentage"] = (item["count"] / total) * 100
        
        return result
    except Exception as e:
        logger.error(f"Failed to get model usage: {e}")
        return []


def get_feature_usage(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get feature usage stats
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of feature usage stats
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if the feature_analytics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feature_analytics'")
        if not cursor.fetchone():
            conn.close()
            return []
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT feature_name, COUNT(*) as count
            FROM feature_analytics
            WHERE timestamp >= ?
            GROUP BY feature_name
            ORDER BY count DESC
        ''', (since_date,))
        feature_data = cursor.fetchall()
        
        conn.close()
        
        result = []
        for feature, count in feature_data:
            result.append({
                "feature": feature,
                "count": count
            })
        
        return result
    except Exception as e:
        logger.error(f"Failed to get feature usage: {e}")
        return []


def get_error_distribution(days: int = 30) -> List[Dict[str, Any]]:
    """
    Get error distribution stats
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of error distribution stats
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if the api_call_analytics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_call_analytics'")
        if not cursor.fetchone():
            conn.close()
            return []
        
        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT error_type, COUNT(*) as count
            FROM api_call_analytics
            WHERE timestamp >= ? AND success = 0 AND error_type IS NOT NULL
            GROUP BY error_type
            ORDER BY count DESC
        ''', (since_date,))
        error_data = cursor.fetchall()
        
        conn.close()
        
        result = []
        for error_type, count in error_data:
            result.append({
                "error_type": error_type,
                "count": count
            })
        
        return result
    except Exception as e:
        logger.error(f"Failed to get error distribution: {e}")
        return []
