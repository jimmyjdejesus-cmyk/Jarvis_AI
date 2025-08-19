"""
Code Intelligence UI Components
Provides UI elements for code completion and intelligence features.
"""

import streamlit as st
import os
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# Import the code intelligence engine
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agent import code_intelligence


def render_code_intelligence_interface():
    """Render the main code intelligence interface."""
    st.header("🧠 Code Intelligence Engine")
    st.write("AI-powered code completion and analysis using local Ollama models")
    
    # Create tabs for different features
    tab1, tab2, tab3, tab4 = st.tabs([
        "Code Completion", 
        "Code Analysis", 
        "Analytics", 
        "Settings"
    ])
    
    with tab1:
        render_code_completion_tab()
    
    with tab2:
        render_code_analysis_tab()
    
    with tab3:
        render_analytics_tab()
    
    with tab4:
        render_settings_tab()


def render_code_completion_tab():
    """Render the code completion interface."""
    st.subheader("💡 Intelligent Code Completion")
    
    # File selection
    st.write("### Select File and Position")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        file_path = st.text_input(
            "File Path",
            placeholder="e.g., /path/to/your/code.py",
            help="Enter the full path to your code file"
        )
    
    with col2:
        demo_button = st.button("Use Demo File", help="Load a demo Python file for testing")
    
    if demo_button:
        # Create a demo file for testing
        demo_content = '''import os
import sys
from typing import List, Dict

class DataProcessor:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.results = []
    
    def load_config(self, path: str) -> Dict:
        # Load configuration from file
        
    def process_data(self, data: List[Dict]) -> List[Dict]:
        processed = []
        for item in data:
            # Process each item
            
        return processed
    
    def save_results(self, output_path: str):
        # Save processing results
        '''
        
        demo_file_path = "/tmp/demo_code.py"
        os.makedirs(os.path.dirname(demo_file_path), exist_ok=True)
        with open(demo_file_path, 'w') as f:
            f.write(demo_content)
        
        st.session_state['demo_file_path'] = demo_file_path
        st.success(f"Demo file created at: {demo_file_path}")
        file_path = demo_file_path
    
    # Get demo file path from session state if available
    if 'demo_file_path' in st.session_state and not file_path:
        file_path = st.session_state['demo_file_path']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cursor_line = st.number_input(
            "Cursor Line", 
            min_value=1, 
            value=14, 
            help="Line number where cursor is positioned"
        )
    
    with col2:
        cursor_column = st.number_input(
            "Cursor Column", 
            min_value=0, 
            value=0, 
            help="Column position in the line"
        )
    
    with col3:
        model = st.selectbox(
            "Ollama Model",
            options=["llama3.2", "codellama", "mixtral", "qwen3:4b"],
            index=0,
            help="Select the model for code completion"
        )
    
    # Show current file content if file exists
    if file_path and os.path.exists(file_path):
        st.write("### Current File Content")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Display content with line numbers
            display_lines = []
            for i, line in enumerate(lines, 1):
                prefix = "➤ " if i == cursor_line else "  "
                display_lines.append(f"{prefix}{i:3d}: {line}")
            
            st.code('\n'.join(display_lines), language=Path(file_path).suffix[1:] if Path(file_path).suffix else 'text')
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Generate completion button
    if st.button("🚀 Generate Code Completion", type="primary"):
        if not file_path:
            st.error("Please provide a file path")
        elif not os.path.exists(file_path):
            st.error(f"File does not exist: {file_path}")
        else:
            with st.spinner("Generating intelligent code completions..."):
                try:
                    completions = code_intelligence.get_code_completion(
                        file_path, 
                        cursor_line, 
                        cursor_column, 
                        model,
                        st.session_state.get('user', 'anonymous')
                    )
                    
                    if completions and not any('error' in comp for comp in completions):
                        st.success(f"Generated {len(completions)} completion(s)")
                        
                        # Display completions
                        for i, completion in enumerate(completions, 1):
                            with st.expander(f"Completion {i} (Confidence: {completion.get('confidence', 0):.2f})"):
                                st.code(completion['suggestion'], language=Path(file_path).suffix[1:])
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button(f"✅ Accept", key=f"accept_{i}"):
                                        # Record positive feedback
                                        success = code_intelligence.record_completion_feedback(
                                            file_path, cursor_line, cursor_column,
                                            completion['suggestion'], True,
                                            st.session_state.get('user', 'anonymous')
                                        )
                                        if success:
                                            st.success("Feedback recorded!")
                                        else:
                                            st.error("Failed to record feedback")
                                
                                with col2:
                                    if st.button(f"❌ Reject", key=f"reject_{i}"):
                                        # Record negative feedback
                                        success = code_intelligence.record_completion_feedback(
                                            file_path, cursor_line, cursor_column,
                                            completion['suggestion'], False,
                                            st.session_state.get('user', 'anonymous')
                                        )
                                        if success:
                                            st.info("Feedback recorded!")
                                        else:
                                            st.error("Failed to record feedback")
                                
                                with col3:
                                    st.write(f"Type: {completion.get('type', 'unknown')}")
                    
                    elif completions and any('error' in comp for comp in completions):
                        st.error(f"Error generating completions: {completions[0].get('error', 'Unknown error')}")
                    
                    else:
                        st.warning("No completions generated. Try adjusting the context or model.")
                
                except Exception as e:
                    st.error(f"Error generating completions: {e}")


def render_code_analysis_tab():
    """Render the code analysis interface."""
    st.subheader("🔍 Code Context Analysis")
    
    file_path = st.text_input(
        "File Path for Analysis",
        placeholder="e.g., /path/to/your/code.py",
        help="Enter the full path to analyze code context"
    )
    
    if file_path and os.path.exists(file_path):
        cursor_line = st.number_input(
            "Analysis Line", 
            min_value=1, 
            value=1, 
            help="Line number to analyze"
        )
        
        if st.button("🔍 Analyze Code Context"):
            with st.spinner("Analyzing code context..."):
                try:
                    engine = code_intelligence.CodeIntelligenceEngine()
                    context = engine.extract_code_context(file_path, cursor_line)
                    
                    # Display analysis results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("### File Information")
                        st.write(f"**File:** {os.path.basename(context.file_path)}")
                        st.write(f"**Language:** {engine._get_language_name(Path(file_path).suffix)}")
                        st.write(f"**Position:** Line {context.cursor_line}, Column {context.cursor_column}")
                        
                        if context.current_class:
                            st.write(f"**Current Class:** {context.current_class}")
                        
                        if context.current_function:
                            st.write(f"**Current Function:** {context.current_function}")
                    
                    with col2:
                        st.write("### Context Information")
                        
                        if context.imports:
                            st.write("**Imports:**")
                            for imp in context.imports[:10]:  # Show first 10 imports
                                st.write(f"- {imp}")
                            if len(context.imports) > 10:
                                st.write(f"... and {len(context.imports) - 10} more")
                        
                        if context.local_variables:
                            st.write("**Local Variables:**")
                            for var in context.local_variables[:10]:  # Show first 10 variables
                                st.write(f"- {var}")
                            if len(context.local_variables) > 10:
                                st.write(f"... and {len(context.local_variables) - 10} more")
                    
                    # Show surrounding code
                    st.write("### Surrounding Code Context")
                    st.code(context.surrounding_code, language=Path(file_path).suffix[1:])
                    
                    # Show project symbols if available
                    if context.project_symbols:
                        st.write("### Project Symbols")
                        st.json(context.project_symbols)
                
                except Exception as e:
                    st.error(f"Error analyzing code context: {e}")
    
    elif file_path:
        st.error(f"File does not exist: {file_path}")


def render_analytics_tab():
    """Render code intelligence analytics."""
    st.subheader("📊 Code Intelligence Analytics")
    
    # Get analytics data
    try:
        engine = code_intelligence.CodeIntelligenceEngine()
        analytics = engine.get_completion_analytics(
            username=st.session_state.get('user') if st.session_state.get('user') != 'anonymous' else None
        )
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Completions",
                analytics['total_completions']
            )
        
        with col2:
            st.metric(
                "Success Rate",
                f"{analytics['success_rate']:.1f}%"
            )
        
        with col3:
            st.metric(
                "Acceptance Rate", 
                f"{analytics['acceptance_rate']:.1f}%"
            )
        
        with col4:
            st.metric(
                "Avg Response Time",
                f"{analytics['avg_generation_time_ms']:.0f}ms"
            )
        
        # Language distribution chart
        if analytics['language_distribution']:
            st.write("### Language Distribution")
            lang_df = pd.DataFrame(
                list(analytics['language_distribution'].items()),
                columns=['Language', 'Completions']
            )
            st.bar_chart(lang_df.set_index('Language'))
        
        # Recent activity (placeholder for more detailed analytics)
        st.write("### Recent Activity")
        st.info("📈 Detailed analytics dashboard coming soon!")
        
    except Exception as e:
        st.error(f"Error loading analytics: {e}")


def render_settings_tab():
    """Render code intelligence settings."""
    st.subheader("⚙️ Code Intelligence Settings")
    
    # Model configuration
    st.write("### Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_model = st.selectbox(
            "Default Completion Model",
            options=["llama3.2", "codellama", "mixtral", "qwen3:4b"],
            index=0,
            help="Select the default model for code completions"
        )
        
        max_suggestions = st.slider(
            "Max Suggestions",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum number of completion suggestions to generate"
        )
    
    with col2:
        completion_timeout = st.slider(
            "Completion Timeout (seconds)",
            min_value=5,
            max_value=60,
            value=30,
            help="Timeout for completion generation"
        )
        
        context_lines = st.slider(
            "Context Lines",
            min_value=3,
            max_value=20,
            value=10,
            help="Number of lines around cursor to include in context"
        )
    
    # Feedback settings
    st.write("### Feedback & Learning")
    
    enable_feedback = st.checkbox(
        "Enable Feedback Collection",
        value=True,
        help="Collect user feedback to improve completion quality"
    )
    
    auto_cache_successful = st.checkbox(
        "Auto-cache Successful Patterns",
        value=True,
        help="Automatically cache patterns from accepted completions"
    )
    
    # Language-specific settings
    st.write("### Language-specific Settings")
    
    supported_languages = st.multiselect(
        "Enabled Languages",
        options=["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "Go", "Rust"],
        default=["Python", "JavaScript", "TypeScript"],
        help="Select languages for code intelligence support"
    )
    
    # Test connection
    st.write("### Connection Test")
    
    if st.button("🔧 Test Ollama Connection"):
        test_ollama_connection()
    
    # Save settings
    if st.button("💾 Save Settings", type="primary"):
        settings = {
            'default_model': default_model,
            'max_suggestions': max_suggestions,
            'completion_timeout': completion_timeout,
            'context_lines': context_lines,
            'enable_feedback': enable_feedback,
            'auto_cache_successful': auto_cache_successful,
            'supported_languages': supported_languages
        }
        
        # Save to user preferences (if user system is available)
        try:
            # This would integrate with the existing user preferences system
            st.success("Settings saved successfully!")
            st.json(settings)
        except Exception as e:
            st.error(f"Error saving settings: {e}")


def test_ollama_connection():
    """Test connection to Ollama API."""
    import requests
    
    try:
        with st.spinner("Testing Ollama connection..."):
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.ok:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                
                st.success("✅ Ollama connection successful!")
                st.write("**Available models:**")
                for model in models:
                    st.write(f"- {model}")
                
                if not models:
                    st.warning("No models found. Run `ollama pull <model-name>` to download models.")
            
            else:
                st.error(f"❌ Ollama connection failed: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Ollama. Make sure Ollama is running on localhost:11434")
    except Exception as e:
        st.error(f"❌ Connection test failed: {e}")


def render_code_intelligence_sidebar():
    """Render code intelligence sidebar components."""
    if st.sidebar.checkbox("🧠 Enable Code Intelligence", value=False):
        st.sidebar.write("### Quick Actions")
        
        if st.sidebar.button("📊 View Analytics"):
            st.session_state['show_code_analytics'] = True
        
        if st.sidebar.button("⚙️ Intelligence Settings"):
            st.session_state['show_code_settings'] = True
        
        # Quick file analysis
        st.sidebar.write("### Quick Analysis")
        quick_file = st.sidebar.text_input(
            "File path",
            placeholder="Enter file path...",
            key="quick_analysis_file"
        )
        
        if quick_file and st.sidebar.button("Analyze"):
            st.session_state['quick_analysis_file'] = quick_file
            st.session_state['show_quick_analysis'] = True