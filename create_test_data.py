#!/usr/bin/env python3
"""Script to populate test data for analytics and feedback features"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
import analytics_tracker
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create test data for analytics and feedback"""
    
    print("Initializing database...")
    database.init_db()
    
    # Test users
    test_users = ['admin', 'testuser1', 'testuser2', 'demo']
    
    print("Creating test API call data...")
    # Create test API call data
    models = ['llama2', 'qwen3:4b', 'gemma:1b', 'mistral']
    endpoints = ['chat', 'rag', 'tool']
    
    for i in range(100):
        username = random.choice(test_users)
        endpoint_type = random.choice(endpoints)
        model_name = random.choice(models)
        
        # Random data
        prompt_tokens = random.randint(10, 500)
        response_tokens = random.randint(50, 1000)
        latency_ms = random.randint(100, 5000)
        success = random.choice([True, True, True, False])  # 75% success rate
        
        database.log_api_call(
            username=username,
            session_id=random.randint(1, 10),
            endpoint_type=endpoint_type,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            latency_ms=latency_ms,
            success=success,
            error_type="timeout_error" if not success else None,
            error_message="Request timeout" if not success else None
        )
    
    print("Creating test feature usage data...")
    # Create test feature usage data
    features = ['chat', 'rag', 'file_upload', 'settings', 'model_selection']
    actions = ['used', 'enabled', 'disabled', 'configured']
    
    for i in range(150):
        username = random.choice(test_users)
        feature = random.choice(features)
        action = random.choice(actions)
        
        database.log_feature_usage(
            username=username,
            feature_name=feature,
            action=action,
            metadata={'test_data': True, 'iteration': i},
            session_id=random.randint(1, 10)
        )
    
    print("Creating test error data...")
    # Create test error data
    error_types = ['api_error', 'validation_error', 'system_error', 'timeout_error']
    
    for i in range(20):
        username = random.choice(test_users)
        error_type = random.choice(error_types)
        
        database.log_error(
            username=username,
            session_id=random.randint(1, 10),
            error_type=error_type,
            error_code=f"E{random.randint(1000, 9999)}",
            error_message=f"Test error message #{i}",
            context={'test_data': True}
        )
    
    print("Creating test feedback data...")
    # Create test feedback data
    feedback_types = ['satisfaction', 'suggestion', 'issue', 'feature_request']
    categories = ['ui', 'performance', 'feature', 'bug', 'documentation']
    priorities = ['low', 'medium', 'high']
    
    feedback_samples = [
        {
            'type': 'satisfaction',
            'title': 'Great AI Assistant!',
            'description': 'I love using Jarvis AI. It helps me a lot with my daily tasks.',
            'rating': 5,
            'category': 'feature'
        },
        {
            'type': 'suggestion',
            'title': 'Add Dark Mode',
            'description': 'It would be great to have a dark mode option for better night usage.',
            'category': 'ui'
        },
        {
            'type': 'issue',
            'title': 'Slow Response Times',
            'description': 'Sometimes the AI takes a very long time to respond.',
            'category': 'performance',
            'priority': 'medium'
        },
        {
            'type': 'feature_request',
            'title': 'Voice Input Support',
            'description': 'Please add voice input support for hands-free interaction.',
            'category': 'feature',
            'priority': 'high'
        },
        {
            'type': 'satisfaction',
            'title': 'Good but could be better',
            'description': 'The AI is helpful but sometimes gives irrelevant answers.',
            'rating': 3,
            'category': 'feature'
        }
    ]
    
    for sample in feedback_samples:
        for username in test_users[:3]:  # Only add for first 3 users
            database.save_user_feedback(
                username=username,
                feedback_type=sample['type'],
                description=sample['description'],
                rating=sample.get('rating'),
                title=sample['title'],
                category=sample['category'],
                priority=sample.get('priority', 'medium')
            )
    
    print("Updating user activity summaries...")
    # Update user activity summaries
    for username in test_users:
        # Update for last 7 days
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            database.update_user_activity_summary(username, date)
    
    print("Test data creation completed!")
    print(f"Created data for users: {', '.join(test_users)}")

if __name__ == "__main__":
    create_test_data()