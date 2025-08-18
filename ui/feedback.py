import streamlit as st
import database
from datetime import datetime


def render_feedback_form():
    """Render user feedback form"""
    st.header("💬 Share Your Feedback")
    
    # Get current user
    username = st.session_state.get("username", "anonymous")
    
    with st.form("feedback_form"):
        # Feedback type
        feedback_type = st.selectbox(
            "Feedback Type",
            ["satisfaction", "suggestion", "issue", "feature_request"],
            format_func=lambda x: {
                "satisfaction": "😊 Satisfaction Rating",
                "suggestion": "💡 Suggestion",
                "issue": "🐛 Report Issue",
                "feature_request": "🚀 Feature Request"
            }[x]
        )
        
        # Title
        title = st.text_input("Title (Optional)", placeholder="Brief summary of your feedback")
        
        # Rating (only for satisfaction feedback)
        rating = None
        if feedback_type == "satisfaction":
            rating = st.select_slider(
                "How satisfied are you with Jarvis AI?",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: "⭐" * x
            )
        
        # Category
        category = st.selectbox(
            "Category",
            ["ui", "performance", "feature", "bug", "documentation", "other"],
            format_func=lambda x: {
                "ui": "🎨 User Interface",
                "performance": "⚡ Performance",
                "feature": "🔧 Feature",
                "bug": "🐛 Bug",
                "documentation": "📚 Documentation",
                "other": "📝 Other"
            }[x]
        )
        
        # Priority (for issues and feature requests)
        priority = "medium"
        if feedback_type in ["issue", "feature_request"]:
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high", "critical"],
                index=1,
                format_func=lambda x: {
                    "low": "🟢 Low",
                    "medium": "🟡 Medium", 
                    "high": "🟠 High",
                    "critical": "🔴 Critical"
                }[x]
            )
        
        # Description
        description = st.text_area(
            "Description",
            placeholder="Please provide detailed feedback...",
            height=150
        )
        
        # Submit button
        submitted = st.form_submit_button("Submit Feedback", type="primary")
        
        if submitted:
            if not description.strip():
                st.error("Please provide a description for your feedback.")
            else:
                # Save feedback to database
                success = database.save_user_feedback(
                    username=username,
                    feedback_type=feedback_type,
                    description=description.strip(),
                    rating=rating,
                    title=title.strip() if title.strip() else None,
                    category=category,
                    priority=priority
                )
                
                if success:
                    st.success("Thank you for your feedback! We appreciate your input.")
                    # Log feature usage
                    database.log_feature_usage(username, "feedback", "submitted", {
                        "feedback_type": feedback_type,
                        "category": category,
                        "priority": priority
                    })
                    st.rerun()
                else:
                    st.error("Failed to submit feedback. Please try again.")


def render_quick_feedback():
    """Render quick feedback widget for sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Feedback")
    
    username = st.session_state.get("username", "anonymous")
    
    # Quick satisfaction rating
    satisfaction = st.sidebar.select_slider(
        "Rate this session:",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: "⭐" * x,
        key="quick_satisfaction"
    )
    
    # Quick feedback text
    quick_feedback = st.sidebar.text_area(
        "Quick feedback:",
        placeholder="Any quick thoughts?",
        height=80,
        key="quick_feedback_text"
    )
    
    if st.sidebar.button("Submit Quick Feedback", key="submit_quick"):
        if quick_feedback.strip():
            success = database.save_user_feedback(
                username=username,
                feedback_type="satisfaction",
                description=quick_feedback.strip(),
                rating=satisfaction,
                title="Quick Feedback",
                category="other",
                priority="low"
            )
            
            if success:
                st.sidebar.success("Feedback submitted!")
                database.log_feature_usage(username, "quick_feedback", "submitted")
                # Clear the text area
                st.session_state.quick_feedback_text = ""
                st.rerun()
            else:
                st.sidebar.error("Failed to submit")


def render_feedback_popup():
    """Render feedback popup that appears periodically"""
    # Check if we should show feedback popup
    if should_show_feedback_popup():
        with st.sidebar:
            with st.container():
                st.markdown("### 💭 How are we doing?")
                st.markdown("Help us improve Jarvis AI!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Give Feedback", key="popup_feedback"):
                        st.session_state.show_feedback_form = True
                        st.session_state.last_feedback_popup = datetime.now().isoformat()
                        st.rerun()
                
                with col2:
                    if st.button("Later", key="popup_later"):
                        st.session_state.last_feedback_popup = datetime.now().isoformat()
                        st.rerun()


def should_show_feedback_popup():
    """Determine if feedback popup should be shown"""
    # Don't show if user has given feedback recently
    if st.session_state.get("show_feedback_form", False):
        return False
    
    # Check if enough time has passed since last popup
    last_popup = st.session_state.get("last_feedback_popup")
    if last_popup:
        try:
            last_time = datetime.fromisoformat(last_popup)
            # Show popup every 24 hours
            if (datetime.now() - last_time).days < 1:
                return False
        except:
            pass
    
    # Check if user has been active enough
    username = st.session_state.get("username")
    if not username:
        return False
    
    # Only show to users who have made at least 5 API calls
    try:
        overview = database.get_analytics_overview(days=1)
        if overview.get('total_api_calls', 0) >= 5:
            return True
    except:
        pass
    
    return False


def render_my_feedback():
    """Render user's own feedback history"""
    st.header("📝 My Feedback History")
    
    username = st.session_state.get("username", "anonymous")
    
    # Get user's feedback
    try:
        conn = database.sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, feedback_type, rating, title, description, category, 
                   priority, status, created_at, updated_at
            FROM user_feedback 
            WHERE username = ?
            ORDER BY created_at DESC
        ''', (username,))
        
        feedback_list = []
        for row in cursor.fetchall():
            feedback_list.append({
                "id": row[0],
                "feedback_type": row[1],
                "rating": row[2],
                "title": row[3],
                "description": row[4],
                "category": row[5],
                "priority": row[6],
                "status": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            })
        
        conn.close()
        
        if feedback_list:
            for feedback in feedback_list:
                status_color = {
                    "open": "🔵",
                    "in_progress": "🟡", 
                    "resolved": "🟢",
                    "closed": "⚫"
                }.get(feedback['status'], "🔵")
                
                with st.expander(f"{status_color} {feedback['feedback_type'].title()}: {feedback.get('title', 'No title')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Type:** {feedback['feedback_type']}")
                        st.write(f"**Category:** {feedback.get('category', 'N/A')}")
                        if feedback.get('rating'):
                            st.write(f"**Rating:** {'⭐' * feedback['rating']}")
                        st.write(f"**Description:** {feedback['description']}")
                    
                    with col2:
                        st.write(f"**Priority:** {feedback.get('priority', 'medium')}")
                        st.write(f"**Status:** {feedback.get('status', 'open')}")
                        st.write(f"**Submitted:** {feedback['created_at']}")
                        if feedback.get('updated_at') != feedback.get('created_at'):
                            st.write(f"**Updated:** {feedback['updated_at']}")
        else:
            st.info("You haven't submitted any feedback yet.")
            if st.button("Submit Your First Feedback"):
                st.session_state.show_feedback_form = True
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading feedback history: {e}")


def render_feedback_stats():
    """Render feedback statistics for users"""
    st.subheader("📊 Feedback Statistics")
    
    username = st.session_state.get("username", "anonymous")
    
    try:
        conn = database.sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        # Get user's feedback statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_feedback,
                AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_count,
                COUNT(CASE WHEN feedback_type = 'satisfaction' THEN 1 END) as satisfaction_count,
                COUNT(CASE WHEN feedback_type = 'suggestion' THEN 1 END) as suggestion_count,
                COUNT(CASE WHEN feedback_type = 'issue' THEN 1 END) as issue_count,
                COUNT(CASE WHEN feedback_type = 'feature_request' THEN 1 END) as feature_request_count
            FROM user_feedback 
            WHERE username = ?
        ''', (username,))
        
        stats = cursor.fetchone()
        conn.close()
        
        if stats and stats[0] > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Feedback", stats[0])
            
            with col2:
                avg_rating = stats[1] if stats[1] else 0
                st.metric("Avg Rating", f"{avg_rating:.1f}⭐")
            
            with col3:
                resolved_rate = (stats[2] / stats[0] * 100) if stats[0] > 0 else 0
                st.metric("Resolved", f"{resolved_rate:.0f}%")
            
            with col4:
                st.metric("This Month", "N/A")  # Could calculate monthly feedback
            
            # Feedback type breakdown
            st.write("**Feedback Breakdown:**")
            breakdown_cols = st.columns(4)
            
            with breakdown_cols[0]:
                st.metric("😊 Satisfaction", stats[4])
            
            with breakdown_cols[1]:
                st.metric("💡 Suggestions", stats[5])
            
            with breakdown_cols[2]:
                st.metric("🐛 Issues", stats[6])
            
            with breakdown_cols[3]:
                st.metric("🚀 Features", stats[7])
        else:
            st.info("No feedback statistics available yet.")
            
    except Exception as e:
        st.error(f"Error loading feedback statistics: {e}")


def render_feedback_interface():
    """Main feedback interface"""
    if st.session_state.get("show_feedback_form", False):
        render_feedback_form()
        
        if st.button("← Back to My Feedback"):
            st.session_state.show_feedback_form = False
            st.rerun()
    else:
        # Tabs for different feedback views
        tab1, tab2 = st.tabs(["📝 My Feedback", "💬 Give Feedback"])
        
        with tab1:
            render_feedback_stats()
            render_my_feedback()
        
        with tab2:
            render_feedback_form()