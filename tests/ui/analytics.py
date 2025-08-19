import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import database


def render_analytics_dashboard():
    """Render the analytics dashboard"""
    st.header("📊 Usage Analytics Dashboard")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    with col1:
        days = st.selectbox("Time Period", [7, 14, 30, 90], index=2)
    
    # Get analytics overview
    overview = database.get_analytics_overview(days=days)
    
    if not overview:
        st.error("Unable to load analytics data")
        return
    
    # Key metrics
    st.subheader("📈 Key Metrics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric("Total API Calls", f"{overview.get('total_api_calls', 0):,}")
    
    with metric_cols[1]:
        st.metric("Active Users", overview.get('active_users', 0))
    
    with metric_cols[2]:
        avg_latency = overview.get('avg_latency_ms', 0)
        st.metric("Avg Latency", f"{avg_latency:.1f}ms")
    
    with metric_cols[3]:
        error_rate = 0
        if overview.get('total_api_calls', 0) > 0:
            error_rate = (overview.get('error_count', 0) / overview.get('total_api_calls', 1)) * 100
        st.metric("Error Rate", f"{error_rate:.1f}%")
    
    # Token usage
    st.subheader("🔤 Token Usage")
    token_cols = st.columns(2)
    
    with token_cols[0]:
        st.metric("Prompt Tokens", f"{overview.get('total_prompt_tokens', 0):,}")
    
    with token_cols[1]:
        st.metric("Response Tokens", f"{overview.get('total_response_tokens', 0):,}")
    
    # Popular features
    st.subheader("⭐ Popular Features")
    popular_features = overview.get('popular_features', [])
    
    if popular_features:
        df_features = pd.DataFrame(popular_features, columns=['Feature', 'Usage Count'])
        fig = px.bar(df_features, x='Feature', y='Usage Count', 
                    title=f"Feature Usage (Last {days} days)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No feature usage data available")
    
    # Error analytics
    st.subheader("🚨 Error Analytics")
    render_error_analytics()
    
    # User feedback summary
    st.subheader("💬 User Feedback Summary")
    feedback_count = overview.get('feedback_count', 0)
    if feedback_count > 0:
        st.metric("New Feedback Items", feedback_count)
        
        # Show recent feedback
        recent_feedback = database.get_user_feedback(limit=5)
        if recent_feedback:
            st.write("**Recent Feedback:**")
            for feedback in recent_feedback:
                with st.expander(f"{feedback['feedback_type'].title()}: {feedback.get('title', 'No title')}"):
                    st.write(f"**User:** {feedback['username']}")
                    st.write(f"**Category:** {feedback.get('category', 'N/A')}")
                    st.write(f"**Priority:** {feedback.get('priority', 'medium')}")
                    if feedback.get('rating'):
                        st.write(f"**Rating:** {'⭐' * feedback['rating']}")
                    st.write(f"**Description:** {feedback['description']}")
                    st.write(f"**Created:** {feedback['created_at']}")
    else:
        st.info("No new feedback in this period")


def render_error_analytics():
    """Render error analytics section"""
    error_data = database.get_error_analytics(days=7)
    
    if error_data:
        df_errors = pd.DataFrame(error_data)
        
        # Error type distribution
        fig = px.pie(df_errors, values='count', names='error_type', 
                    title="Error Distribution (Last 7 days)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Error details table
        st.write("**Error Details:**")
        st.dataframe(df_errors, use_container_width=True)
    else:
        st.success("No errors in the last 7 days! 🎉")


def render_user_analytics():
    """Render user-specific analytics"""
    st.header("👤 User Analytics")
    
    # User selector (for admins)
    is_admin = st.session_state.get("is_admin", False)
    username = st.session_state.get("username", "default")
    
    if is_admin:
        # Get all users for admin view
        all_users = database.get_all_users()
        if all_users:
            usernames = [user['username'] for user in all_users]
            selected_user = st.selectbox("Select User", usernames, 
                                       index=usernames.index(username) if username in usernames else 0)
        else:
            selected_user = username
    else:
        selected_user = username
        st.info(f"Viewing analytics for: {selected_user}")
    
    # Time period
    days = st.selectbox("Time Period", [7, 14, 30, 90], index=1, key="user_analytics_days")
    
    # Get user-specific analytics
    render_user_activity_chart(selected_user, days)
    render_user_feature_usage(selected_user, days)


def render_user_activity_chart(username: str, days: int):
    """Render user activity chart"""
    st.subheader("📊 Activity Over Time")
    
    try:
        # Get daily activity data
        conn = database.sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).date()
        
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as api_calls,
                   AVG(latency_ms) as avg_latency
            FROM api_call_analytics 
            WHERE username = ? AND DATE(timestamp) >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (username, since_date))
        
        activity_data = cursor.fetchall()
        conn.close()
        
        if activity_data:
            df = pd.DataFrame(activity_data, columns=['Date', 'API Calls', 'Avg Latency'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Create subplot with two y-axes
            fig = go.Figure()
            
            # API calls
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['API Calls'],
                mode='lines+markers',
                name='API Calls',
                line=dict(color='blue')
            ))
            
            fig.update_layout(
                title=f"Daily Activity for {username}",
                xaxis_title="Date",
                yaxis_title="API Calls",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No activity data found for {username} in the last {days} days")
            
    except Exception as e:
        st.error(f"Error loading user activity data: {e}")


def render_user_feature_usage(username: str, days: int):
    """Render user feature usage"""
    st.subheader("🔧 Feature Usage")
    
    try:
        conn = database.sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT feature_name, action, COUNT(*) as usage_count
            FROM feature_analytics 
            WHERE username = ? AND timestamp >= ?
            GROUP BY feature_name, action
            ORDER BY usage_count DESC
        ''', (username, since_date))
        
        feature_data = cursor.fetchall()
        conn.close()
        
        if feature_data:
            df = pd.DataFrame(feature_data, columns=['Feature', 'Action', 'Usage Count'])
            
            # Feature usage bar chart
            fig = px.bar(df, x='Feature', y='Usage Count', color='Action',
                        title=f"Feature Usage for {username} (Last {days} days)")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature usage table
            st.write("**Detailed Feature Usage:**")
            st.dataframe(df, use_container_width=True)
        else:
            st.info(f"No feature usage data found for {username} in the last {days} days")
            
    except Exception as e:
        st.error(f"Error loading feature usage data: {e}")


def render_feedback_management():
    """Render feedback management interface"""
    st.header("💬 Feedback Management")
    
    # Feedback status filter
    status_filter = st.selectbox("Filter by Status", 
                               ["all", "open", "in_progress", "resolved", "closed"],
                               index=0)
    
    status = None if status_filter == "all" else status_filter
    feedback_list = database.get_user_feedback(limit=100, status=status)
    
    if feedback_list:
        for feedback in feedback_list:
            with st.expander(f"#{feedback['id']} - {feedback['feedback_type'].title()}: {feedback.get('title', 'No title')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**User:** {feedback['username']}")
                    st.write(f"**Type:** {feedback['feedback_type']}")
                    st.write(f"**Category:** {feedback.get('category', 'N/A')}")
                    if feedback.get('rating'):
                        st.write(f"**Rating:** {'⭐' * feedback['rating']}")
                    st.write(f"**Description:** {feedback['description']}")
                    st.write(f"**Created:** {feedback['created_at']}")
                
                with col2:
                    st.write(f"**Priority:** {feedback.get('priority', 'medium')}")
                    st.write(f"**Status:** {feedback.get('status', 'open')}")
                    
                    # Admin actions
                    if st.session_state.get("is_admin", False):
                        new_status = st.selectbox("Update Status", 
                                                ["open", "in_progress", "resolved", "closed"],
                                                index=["open", "in_progress", "resolved", "closed"].index(feedback.get('status', 'open')),
                                                key=f"status_{feedback['id']}")
                        
                        if st.button("Update", key=f"update_{feedback['id']}"):
                            if database.update_feedback_status(feedback['id'], new_status):
                                st.success("Status updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update status")
    else:
        st.info("No feedback found")


def render_system_health():
    """Render system health monitoring"""
    st.header("🏥 System Health")
    
    # Recent errors
    st.subheader("Recent Errors")
    render_error_analytics()
    
    # System metrics
    st.subheader("System Metrics")
    
    # Get recent system activity
    overview = database.get_analytics_overview(days=1)
    
    if overview:
        health_cols = st.columns(3)
        
        with health_cols[0]:
            st.metric("API Calls (24h)", overview.get('total_api_calls', 0))
        
        with health_cols[1]:
            avg_latency = overview.get('avg_latency_ms', 0)
            status = "🟢" if avg_latency < 1000 else "🟡" if avg_latency < 3000 else "🔴"
            st.metric("Avg Latency", f"{avg_latency:.1f}ms {status}")
        
        with health_cols[2]:
            error_rate = 0
            if overview.get('total_api_calls', 0) > 0:
                error_rate = (overview.get('error_count', 0) / overview.get('total_api_calls', 1)) * 100
            status = "🟢" if error_rate < 1 else "🟡" if error_rate < 5 else "🔴"
            st.metric("Error Rate", f"{error_rate:.1f}% {status}")
    
    # Performance trends
    st.subheader("Performance Trends")
    render_performance_trends()


def render_performance_trends():
    """Render performance trends chart"""
    try:
        conn = database.sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        # Get hourly performance data for the last 24 hours
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as api_calls,
                AVG(latency_ms) as avg_latency,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as error_rate
            FROM api_call_analytics 
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp)
            ORDER BY hour
        ''')
        
        perf_data = cursor.fetchall()
        conn.close()
        
        if perf_data:
            df = pd.DataFrame(perf_data, columns=['Hour', 'API Calls', 'Avg Latency', 'Error Rate'])
            df['Hour'] = pd.to_datetime(df['Hour'])
            
            # Create multi-line chart
            fig = go.Figure()
            
            # API calls
            fig.add_trace(go.Scatter(
                x=df['Hour'], y=df['API Calls'],
                mode='lines+markers',
                name='API Calls',
                yaxis='y'
            ))
            
            # Average latency
            fig.add_trace(go.Scatter(
                x=df['Hour'], y=df['Avg Latency'],
                mode='lines+markers',
                name='Avg Latency (ms)',
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="Performance Trends (Last 24 Hours)",
                xaxis_title="Hour",
                yaxis=dict(title="API Calls", side="left"),
                yaxis2=dict(title="Latency (ms)", side="right", overlaying="y"),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No performance data available for the last 24 hours")
            
    except Exception as e:
        st.error(f"Error loading performance trends: {e}")