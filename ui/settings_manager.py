"""
UI-based Configuration Manager for Jarvis AI
Provides a Streamlit interface for managing configuration settings
"""

import streamlit as st
import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add legacy directory to path for imports
current_dir = Path(__file__).parent.parent
legacy_dir = current_dir / "legacy"
sys.path.insert(0, str(legacy_dir))

try:
    from agent.core.config_manager import get_config_manager, JarvisConfig
except ImportError:
    # Fallback if imports not available
    get_config_manager = None
    JarvisConfig = None


def render_settings_manager():
    """Render the UI-based settings manager."""
    if get_config_manager is None:
        st.error("Configuration manager not available")
        return
    
    st.title("⚙️ Jarvis AI Settings Manager")
    st.markdown("Configure your Jarvis AI deployment and distribution settings")
    
    config_manager = get_config_manager()
    
    try:
        config = config_manager.load_config()
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return
    
    # Create tabs for different configuration sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔧 General", 
        "🔒 Security", 
        "🚀 Deployment", 
        "🤖 Lang Ecosystem", 
        "📁 Advanced"
    ])
    
    with tab1:
        render_general_settings(config)
    
    with tab2:
        render_security_settings(config)
    
    with tab3:
        render_deployment_settings(config)
    
    with tab4:
        render_lang_ecosystem_settings(config)
    
    with tab5:
    # Configuration-driven tab creation
    tab_configs = [
        {"name": "🔧 General", "render_func": render_general_settings},
        {"name": "🔒 Security", "render_func": render_security_settings},
        {"name": "🚀 Deployment", "render_func": render_deployment_settings},
        {"name": "🤖 Lang Ecosystem", "render_func": render_lang_ecosystem_settings},
        {"name": "📁 Advanced", "render_func": render_advanced_settings},
    ]
    tabs = st.tabs([tab["name"] for tab in tab_configs])
    for tab, tab_config in zip(tabs, tab_configs):
        with tab:
            tab_config["render_func"](config)
    
    # Save configuration button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            save_configuration(config)


def render_general_settings(config: 'JarvisConfig'):
    """Render general application settings."""
    st.header("General Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config.app_name = st.text_input("Application Name", value=config.app_name)
        config.debug_mode = st.checkbox("Debug Mode", value=config.debug_mode)
        config.data_directory = st.text_input("Data Directory", value=config.data_directory)
    
    with col2:
        config.logs_directory = st.text_input("Logs Directory", value=config.logs_directory)
        config.plugins_directory = st.text_input("Plugins Directory", value=config.plugins_directory)
    
    # Integrations
    st.subheader("Integrations")
    col1, col2 = st.columns(2)
    
    with col1:
        config.integrations.ollama_endpoint = st.text_input(
            "Ollama Endpoint", 
            value=config.integrations.ollama_endpoint,
            help="URL for your local Ollama instance"
        )
        config.integrations.default_model = st.text_input(
            "Default Model", 
            value=config.integrations.default_model
        )
    
    with col2:
        config.integrations.enable_github = st.checkbox(
            "Enable GitHub Integration", 
            value=config.integrations.enable_github
        )
        if config.integrations.enable_github:
            github_token = st.text_input(
                "GitHub Token", 
                value=config.integrations.github_token or "",
                type="password",
                help="Set via JARVIS_GITHUB_TOKEN environment variable"
            )
            if github_token:
                config.integrations.github_token = github_token


def render_security_settings(config: 'JarvisConfig'):
    """Render security settings."""
    st.header("Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config.security.session_timeout_minutes = st.number_input(
            "Session Timeout (minutes)", 
            value=config.security.session_timeout_minutes,
            min_value=5,
            max_value=1440
        )
        config.security.max_login_attempts = st.number_input(
            "Max Login Attempts", 
            value=config.security.max_login_attempts,
            min_value=1,
            max_value=10
        )
    
    with col2:
        config.security.login_lockout_minutes = st.number_input(
            "Login Lockout (minutes)", 
            value=config.security.login_lockout_minutes,
            min_value=1,
            max_value=60
        )
        config.security.password_min_length = st.number_input(
            "Minimum Password Length", 
            value=config.security.password_min_length,
            min_value=6,
            max_value=20
        )
    
    config.security.require_special_chars = st.checkbox(
        "Require Special Characters in Passwords", 
        value=config.security.require_special_chars
    )


def render_deployment_settings(config: 'JarvisConfig'):
    """Render deployment and distribution settings."""
    st.header("Deployment Settings")
    
    # Docker settings
    st.subheader("🐳 Docker Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        docker_enabled = st.checkbox("Enable Docker Deployment", value=True)
        if docker_enabled:
            st.info("Use 'docker-compose up' to start with Ollama")
    
    with col2:
        docker_port = st.number_input("Docker Port", value=8501, min_value=1000, max_value=65535)
        st.code(f"docker run -p {docker_port}:8501 jarvis-ai")
    
    # Package installation
    st.subheader("📦 Package Installation")
    st.info("Install via pip: `pip install jarvis-ai`")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Development Installation:**")
        st.code("pip install -e .")
    
    with col2:
        st.markdown("**One-click Installer:**")
        st.markdown("Run `scripts/installers/install-unix.sh` for automated setup")
    
    # Performance settings
    st.subheader("⚡ Performance")
    col1, col2 = st.columns(2)
    
    with col1:
        config.performance.enable_caching = st.checkbox(
            "Enable Caching", 
            value=config.performance.enable_caching
        )
        config.performance.cache_size_mb = st.number_input(
            "Cache Size (MB)", 
            value=config.performance.cache_size_mb,
            min_value=50,
            max_value=2048
        )
    
    with col2:
        config.performance.max_concurrent_requests = st.number_input(
            "Max Concurrent Requests", 
            value=config.performance.max_concurrent_requests,
            min_value=1,
            max_value=50
        )


def render_lang_ecosystem_settings(config: 'JarvisConfig'):
    """Render Lang ecosystem configuration."""
    st.header("Lang Ecosystem Integration")
    
    # LangSmith settings
    st.subheader("🔍 LangSmith (Tracing & Monitoring)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config.lang_ecosystem.langsmith.enabled = st.checkbox(
            "Enable LangSmith", 
            value=config.lang_ecosystem.langsmith.enabled,
            help="Enable tracing and monitoring for deployments"
        )
        
        if config.lang_ecosystem.langsmith.enabled:
            config.lang_ecosystem.langsmith.project_name = st.text_input(
                "Project Name", 
                value=config.lang_ecosystem.langsmith.project_name
            )
    
    with col2:
        if config.lang_ecosystem.langsmith.enabled:
            langsmith_api_key = st.text_input(
                "LangSmith API Key", 
                value=config.lang_ecosystem.langsmith.api_key or "",
                type="password",
                help="Set via LANGSMITH_API_KEY environment variable"
            )
            if langsmith_api_key:
                config.lang_ecosystem.langsmith.api_key = langsmith_api_key
    
    # LangGraph Platform settings
    st.subheader("🚀 LangGraph Platform")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config.lang_ecosystem.langgraph_platform.enabled = st.checkbox(
            "Enable LangGraph Platform", 
            value=config.lang_ecosystem.langgraph_platform.enabled,
            help="Enable team collaboration and agent sharing"
        )
        
        if config.lang_ecosystem.langgraph_platform.enabled:
            config.lang_ecosystem.langgraph_platform.deployment_environment = st.selectbox(
                "Deployment Environment",
                ["development", "staging", "production"],
                index=["development", "staging", "production"].index(
                    config.lang_ecosystem.langgraph_platform.deployment_environment
                )
            )
    
    with col2:
        if config.lang_ecosystem.langgraph_platform.enabled:
            langgraph_api_key = st.text_input(
                "LangGraph Platform API Key", 
                value=config.lang_ecosystem.langgraph_platform.api_key or "",
                type="password"
            )
            if langgraph_api_key:
                config.lang_ecosystem.langgraph_platform.api_key = langgraph_api_key
            
            config.lang_ecosystem.langgraph_platform.workspace_id = st.text_input(
                "Workspace ID", 
                value=config.lang_ecosystem.langgraph_platform.workspace_id or ""
            )
    
    # Deployment monitoring
    st.subheader("📊 Deployment Monitoring")
    col1, col2 = st.columns(2)
    
    with col1:
        config.lang_ecosystem.deployment.enable_telemetry = st.checkbox(
            "Enable Telemetry", 
            value=config.lang_ecosystem.deployment.enable_telemetry
        )
        config.lang_ecosystem.deployment.performance_tracking = st.checkbox(
            "Performance Tracking", 
            value=config.lang_ecosystem.deployment.performance_tracking
        )
    
    with col2:
        config.lang_ecosystem.deployment.error_tracking = st.checkbox(
            "Error Tracking", 
            value=config.lang_ecosystem.deployment.error_tracking
        )


def render_advanced_settings(config: 'JarvisConfig'):
    """Render advanced configuration settings."""
    st.header("Advanced Settings")
    
    # Environment variables section
    st.subheader("🌍 Environment Variables")
    
    env_vars = {
        "JARVIS_DEBUG": "Enable debug mode",
        "JARVIS_V2_ENABLED": "Enable V2 LangGraph architecture",
        "LANGSMITH_API_KEY": "LangSmith API key for tracing",
        "LANGGRAPH_PLATFORM_API_KEY": "LangGraph Platform API key",
        "JARVIS_OLLAMA_ENDPOINT": "Ollama endpoint URL",
        "JARVIS_DEPLOYMENT_TELEMETRY": "Enable deployment telemetry",
    }
    
    st.markdown("**Available Environment Variables:**")
    for var, description in env_vars.items():
        current_value = os.getenv(var, "Not set")
        st.markdown(f"- `{var}`: {description}")
        st.markdown(f"  Current value: `{current_value}`")
    
    # Custom configuration
    st.subheader("🔧 Custom Configuration")
    
    custom_config = st.text_area(
        "Custom YAML Configuration",
        value=yaml.dump(config.custom, default_flow_style=False) if config.custom else "",
        height=150,
        help="Add custom configuration in YAML format"
    )
    
    if custom_config:
        try:
            config.custom = yaml.safe_load(custom_config) or {}
        except yaml.YAMLError as e:
            st.error(f"Invalid YAML: {e}")


def save_configuration(config: 'JarvisConfig'):
    """Save configuration to file."""
    try:
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        config_path = config_dir / "config.yaml"
        
        # Convert config to dictionary for YAML serialization
        config_dict = {
            "app_name": config.app_name,
            "version": config.version,
            "debug_mode": config.debug_mode,
            "data_directory": config.data_directory,
            "logs_directory": config.logs_directory,
            "plugins_directory": config.plugins_directory,
            "security": {
                "session_timeout_minutes": config.security.session_timeout_minutes,
                "max_login_attempts": config.security.max_login_attempts,
                "login_lockout_minutes": config.security.login_lockout_minutes,
                "password_min_length": config.security.password_min_length,
                "require_special_chars": config.security.require_special_chars,
            },
            "performance": {
                "enable_caching": config.performance.enable_caching,
                "cache_size_mb": config.performance.cache_size_mb,
                "max_concurrent_requests": config.performance.max_concurrent_requests,
            },
            "integrations": {
                "ollama_endpoint": config.integrations.ollama_endpoint,
                "default_model": config.integrations.default_model,
                "enable_github": config.integrations.enable_github,
                # Don't save tokens to file, use environment variables
            },
            "lang_ecosystem": {
                "langsmith": {
                    "enabled": config.lang_ecosystem.langsmith.enabled,
                    "project_name": config.lang_ecosystem.langsmith.project_name,
                    "endpoint": config.lang_ecosystem.langsmith.endpoint,
                    "trace_deployments": config.lang_ecosystem.langsmith.trace_deployments,
                    "trace_performance": config.lang_ecosystem.langsmith.trace_performance,
                },
                "langgraph_platform": {
                    "enabled": config.lang_ecosystem.langgraph_platform.enabled,
                    "workspace_id": config.lang_ecosystem.langgraph_platform.workspace_id,
                    "enable_sharing": config.lang_ecosystem.langgraph_platform.enable_sharing,
                    "enable_collaboration": config.lang_ecosystem.langgraph_platform.enable_collaboration,
                    "deployment_environment": config.lang_ecosystem.langgraph_platform.deployment_environment,
                },
                "deployment": {
                    "enable_telemetry": config.lang_ecosystem.deployment.enable_telemetry,
                    "performance_tracking": config.lang_ecosystem.deployment.performance_tracking,
                    "error_tracking": config.lang_ecosystem.deployment.error_tracking,
                }
            },
            "custom": config.custom,
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        
        st.success(f"✅ Configuration saved to {config_path}")
        st.info("🔄 Restart the application to apply changes")
        
    except Exception as e:
        st.error(f"❌ Failed to save configuration: {e}")


def show_deployment_status():
    """Show current deployment status and options."""
    st.header("🚀 Deployment Status")
    
    # Check if running in Docker
    if os.path.exists("/.dockerenv"):
        st.success("🐳 Running in Docker container")
    else:
        st.info("💻 Running locally")
    
    # Show environment info
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}")
        st.metric("Platform", sys.platform)
    
    with col2:
        # Check for key environment variables
        langsmith_configured = "✅" if os.getenv("LANGSMITH_API_KEY") else "❌"
        st.metric("LangSmith Configured", langsmith_configured)
        
        docker_available = "✅" if os.system("docker --version > /dev/null 2>&1") == 0 else "❌"
        st.metric("Docker Available", docker_available)


if __name__ == "__main__":
    render_settings_manager()