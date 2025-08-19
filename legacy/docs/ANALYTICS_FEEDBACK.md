# Usage Analytics and User Feedback System

This document describes the comprehensive analytics and feedback system implemented for Jarvis AI.

## Overview

The system provides detailed usage analytics, error tracking, and user feedback mechanisms to help administrators monitor system performance and gather user insights.

## Features Implemented

### 1. Database Schema

New tables added to track analytics and feedback:

- **`api_call_analytics`**: Tracks all API/model calls with metrics
- **`user_feedback`**: Stores user feedback and satisfaction ratings
- **`feature_analytics`**: Tracks feature usage patterns
- **`error_analytics`**: Logs and categorizes system errors
- **`user_activity_summary`**: Daily activity summaries for quick insights

### 2. Analytics Dashboard (Admin Only)

Access via: Admin Options → 📊 Analytics Dashboard

**Key Metrics Panel:**
- Total API calls
- Active users count
- Average latency
- Error rate percentage
- Token usage (prompt/response)

**Popular Features Chart:**
- Bar chart showing most-used features
- Time period filtering (7, 14, 30, 90 days)

**Error Analytics:**
- Error type distribution (pie chart)
- Error details table
- Recent error tracking

**User Analytics:**
- Individual user activity charts
- Feature usage patterns
- Performance metrics per user

**System Health Monitoring:**
- Real-time performance metrics
- Performance trends over time
- System status indicators

### 3. User Feedback System

**Quick Feedback Widget (Sidebar):**
- Star rating slider (1-5 stars)
- Quick text feedback
- One-click submission

**Detailed Feedback Form:**
- Multiple feedback types: Satisfaction, Suggestion, Issue, Feature Request
- Category selection: UI, Performance, Feature, Bug, Documentation
- Priority levels: Low, Medium, High, Critical
- Structured data collection

**My Feedback History:**
- View submitted feedback
- Track feedback status
- Personal feedback statistics

### 4. Feedback Management (Admin Only)

Access via: Admin Options → 💬 Feedback Management

- View all user feedback
- Filter by status (open, in-progress, resolved, closed)
- Update feedback status
- Assign feedback to team members
- Resolve and close feedback items

### 5. Enhanced API/Model Call Logging

**Automatic Tracking:**
- All API calls logged with detailed metrics
- Token counting (estimated)
- Latency measurement
- Success/failure tracking
- Error classification

**Analytics Integration:**
- Real-time metrics collection
- Daily activity summaries
- Performance trend analysis
- Error pattern detection

## Usage Instructions

### For Users

1. **Quick Feedback:**
   - Use the sidebar widget for quick ratings and comments
   - Rate your session experience with stars
   - Leave brief feedback in the text area

2. **Detailed Feedback:**
   - Access via User Options → 📝 Give Feedback
   - Choose appropriate feedback type and category
   - Provide detailed descriptions
   - Set priority for issues and feature requests

3. **View Your Feedback:**
   - Track your submitted feedback history
   - See feedback status updates
   - View response statistics

### For Administrators

1. **Monitor Usage:**
   - Review analytics dashboard regularly
   - Track user engagement patterns
   - Monitor system performance metrics

2. **Manage Feedback:**
   - Review incoming user feedback
   - Prioritize and assign feedback items
   - Update status as issues are resolved

3. **System Health:**
   - Monitor error rates and types
   - Track performance trends
   - Identify areas for improvement

## Technical Implementation

### Analytics Tracking

The `analytics_tracker.py` module provides:

```python
# Track API calls
@track_api_call(endpoint_type="chat", model_name="llama2")
def my_api_function():
    pass

# Track feature usage
@track_feature_usage(feature_name="rag", action="enabled")
def enable_rag():
    pass

# Context manager for complex operations
with AnalyticsContext(username, "file_upload") as ctx:
    ctx.add_metadata(file_count=5, file_types=["pdf", "txt"])
    # perform operation
```

### Database Functions

Key database functions for analytics:

- `log_api_call()`: Record API call metrics
- `log_feature_usage()`: Track feature interactions
- `log_error()`: Record system errors
- `save_user_feedback()`: Store user feedback
- `get_analytics_overview()`: Generate analytics summaries

### UI Components

- `ui/analytics.py`: Analytics dashboard components
- `ui/feedback.py`: User feedback interfaces
- Integration in `app.py` for admin/user access

## Data Privacy and Security

- All analytics data is stored locally in the SQLite database
- User feedback is associated with usernames for follow-up
- No external analytics services used
- Admins have full control over data retention

## Future Enhancements

Planned improvements:
- Export analytics data to CSV/JSON
- Email notifications for critical feedback
- Advanced filtering and search
- Custom dashboard widgets
- Integration with external monitoring tools
- Automated report generation

## Test Data

Use `create_test_data.py` to populate sample analytics and feedback data for testing and demonstration purposes.

## Access Control

- **Analytics Dashboard**: Admin users only
- **Feedback Management**: Admin users only  
- **Quick Feedback**: All authenticated users
- **Detailed Feedback**: All authenticated users
- **Feedback History**: Users can only see their own feedback

This system provides comprehensive insights into user behavior, system performance, and user satisfaction to help improve the Jarvis AI platform continuously.