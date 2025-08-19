# System Resource Monitoring for Jarvis AI
# Add this to your app.py if concerned about hardware stress

import psutil
import streamlit as st

def check_system_resources():
    """Monitor system resources and warn if usage is high"""
    
    # Get system stats
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Display in sidebar
    with st.sidebar:
        st.markdown("### 🖥️ System Resources")
        
        # CPU usage
        cpu_color = "🔴" if cpu_percent > 80 else "🟡" if cpu_percent > 60 else "🟢"
        st.metric(f"{cpu_color} CPU Usage", f"{cpu_percent}%", delta=None)
        
        # Memory usage
        mem_percent = memory.percent
        mem_color = "🔴" if mem_percent > 80 else "🟡" if mem_percent > 60 else "🟢"
        st.metric(f"{mem_color} Memory Usage", f"{mem_percent}%", delta=None)
        
        # Disk usage
        disk_percent = (disk.used / disk.total) * 100
        disk_color = "🔴" if disk_percent > 90 else "🟡" if disk_percent > 75 else "🟢"
        st.metric(f"{disk_color} Disk Usage", f"{disk_percent:.1f}%", delta=None)
        
        # Warning if resources are high
        if cpu_percent > 80 or mem_percent > 80:
            st.warning("⚠️ High system resource usage detected!")
            st.info("Consider closing other applications or using a smaller model.")

# Add this to your main app
if __name__ == "__main__":
    # Call this in your main app loop
    check_system_resources()
