import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
from database.analytics_functions import (
    get_analytics_overview,
    get_daily_usage,
    get_model_usage,
    get_feature_usage,
    get_error_distribution
)


def render_analytics_dashboard():
    """Render the analytics dashboard"""
    st.header("📊 Usage Analytics Dashboard")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    with col1:
        days = st.selectbox("Time Period", [7, 14, 30, 90], index=2)
    
    # Get analytics overview
    overview = get_analytics_overview(days=days)
    
    # Display analytics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Conversations", overview.get("total_conversations", 0))
    with col2:
        st.metric("Total Messages", overview.get("total_messages", 0))
    with col3:
        st.metric("Active Users", overview.get("active_users", 0))
    with col4:
        st.metric("Avg. Response Time", f"{overview.get('avg_response_time', 0):.2f}s")

    # Show usage over time chart
    st.subheader("Usage Trends")
    
    daily_usage = get_daily_usage(days=days)
    if not daily_usage:
        st.info("No usage data available for the selected period.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(daily_usage)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add conversations line
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df['conversations'],
            name='Conversations',
            line=dict(color='#1f77b4', width=2)
        ))
        
        # Add messages line
        fig.add_trace(go.Scatter(
            x=df['date'], 
            y=df['messages'],
            name='Messages',
            line=dict(color='#ff7f0e', width=2, dash='dot')
        ))
        
        # Layout
        fig.update_layout(
            title='Daily Conversations and Messages',
            xaxis_title='Date',
            yaxis_title='Count',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Model usage statistics
    st.subheader("Model Usage Distribution")
    
    model_usage = get_model_usage(days=days)
    if not model_usage:
        st.info("No model usage data available for the selected period.")
    else:
        # Convert to DataFrame
        df_models = pd.DataFrame(model_usage)
        
        # Create a pie chart
        fig = px.pie(
            df_models, 
            values='count', 
            names='model', 
            title='Model Distribution',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h")
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Feature usage statistics
    st.subheader("Feature Usage")
    
    feature_usage = get_feature_usage(days=days)
    if not feature_usage:
        st.info("No feature usage data available for the selected period.")
    else:
        # Convert to DataFrame
        df_features = pd.DataFrame(feature_usage)
        
        # Create horizontal bar chart
        fig = px.bar(
            df_features,
            x='count',
            y='feature',
            orientation='h',
            title='Feature Usage Count',
            color='count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title='Usage Count',
            yaxis_title='Feature',
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # User activity analysis
    st.subheader("User Activity Analysis")
    
    # Simplified user activity implementation
    user_activity = []
    st.info("User activity tracking is not available in this version.")
    if not user_activity:
        st.info("No user activity data available for the selected period.")
    else:
        # Convert to DataFrame
        df_users = pd.DataFrame(user_activity)
        df_users['username'] = df_users['username'].apply(lambda x: f"{x[:3]}{'*' * (len(x)-3)}" if len(x) > 3 else x)
        
        # Create bubble chart
        fig = px.scatter(
            df_users,
            x='sessions',
            y='messages',
            size='total_time',
            color='role',
            hover_name='username',
            title='User Activity Distribution',
            labels={
                'sessions': 'Number of Sessions',
                'messages': 'Messages Sent',
                'total_time': 'Total Time (min)'
            }
        )
        
        fig.update_layout(
            xaxis_title='Number of Sessions',
            yaxis_title='Messages Sent',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Response time analysis
    st.subheader("Response Time Analysis")
    
    # Simplified response time implementation
    response_times = []
    st.info("Response time analysis is not available in this version.")
    if not response_times:
        st.info("No response time data available for the selected period.")
    else:
        # Convert to DataFrame
        df_times = pd.DataFrame(response_times)
        df_times['time'] = pd.to_datetime(df_times['time'])
        
        # Create line chart
        fig = go.Figure()
        
        # Add average response time
        fig.add_trace(go.Scatter(
            x=df_times['time'], 
            y=df_times['avg_time'],
            name='Average Response Time',
            line=dict(color='#2ca02c', width=2)
        ))
        
        # Add 90th percentile
        fig.add_trace(go.Scatter(
            x=df_times['time'], 
            y=df_times['p90_time'],
            name='90th Percentile',
            line=dict(color='#d62728', width=2, dash='dot')
        ))
        
        # Layout
        fig.update_layout(
            title='Response Time Trends',
            xaxis_title='Time',
            yaxis_title='Response Time (seconds)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Error rates
    st.subheader("System Health")
    
    # Use our error distribution function
    error_rates = get_error_distribution(days=days)
    # Simplify for now
    st.info("Error rate tracking is not available in this version.")
    if not error_rates:
        st.info("No error rate data available for the selected period.")
    else:
        # Convert to DataFrame
        df_errors = pd.DataFrame(error_rates)
        df_errors['date'] = pd.to_datetime(df_errors['date'])
        
        # Create bar chart
        fig = px.bar(
            df_errors,
            x='date',
            y='error_rate',
            title='Daily Error Rate (%)',
            color='error_rate',
            color_continuous_scale='RdYlGn_r'  # Red for high error rates, green for low
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Error Rate (%)',
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        # Add threshold line at 5%
        fig.add_shape(
            type='line',
            x0=df_errors['date'].min(),
            x1=df_errors['date'].max(),
            y0=5,
            y1=5,
            line=dict(
                color='red',
                width=2,
                dash='dash',
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Download raw data option
    st.subheader("Export Data")
    
    # Simple CSV generation for export
    export_data = "Date,Conversations,Messages\n"
    for day in get_daily_usage(days=days):
        export_data += f"{day['date']},{day['conversations']},{day['messages']}\n"
    
    if st.download_button(
        label="Download Analytics Data (CSV)",
        data=export_data,
        file_name=f"jarvis_analytics_{days}d_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    ):
        st.success("Data downloaded successfully!")
