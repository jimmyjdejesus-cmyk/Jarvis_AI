import streamlit as st
import uuid
import json
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))

from ollama_client import get_available_models


def auto_chat_name(context):
    if not context:
        return "New Chat"
    context = context.strip()
    if len(context) > 40:
        context = context[:37] + "..."
    return context.replace("\n", " ") or "New Chat"

def sidebar(user, save_user_prefs):
    from database.database import get_user_preferences, save_user_preference, get_user_settings, save_user_settings
    from database.admin_utils import backup_user_data, import_user_data, backup_all_user_data, import_user_data_from_json
    with st.sidebar:
        st.markdown(f"### 👤 User: `{user}`")
        st.markdown("## 📁 Projects & Chats")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        if "current_chat" not in st.session_state:
            st.session_state["current_chat"] = None
        if "chats" not in st.session_state:
            st.session_state["chats"] = {}
            
        # Initialize chat sessions (for backward compatibility)
        if "chat_sessions" not in st.session_state:
            st.session_state["chat_sessions"] = {"Default": []}
        if "current_session" not in st.session_state:
            st.session_state["current_session"] = "Default"
        
        # Get user preferences
        user_prefs = get_user_preferences(user)
        
        # Create new chat button
        if st.button("➕ New Chat"):
            chat_id = str(uuid.uuid4())
            st.session_state["current_chat"] = chat_id
            st.session_state["chat_history"] = []
            st.session_state["chats"][chat_id] = {
                "id": chat_id,
                "title": "New Chat",
                "messages": []
            }
            save_user_prefs()
            st.rerun()

        # List existing chats
        if st.session_state["chats"]:
            st.write("### Recent Chats")
            for chat_id, chat in st.session_state["chats"].items():
                chat_title = chat.get("title", "Unnamed Chat")
                if st.button(f"💬 {chat_title}", key=f"chat_{chat_id}"):
                    st.session_state["current_chat"] = chat_id
                    st.session_state["chat_history"] = chat.get("messages", [])
                    st.rerun()
                    
        # System settings section
        st.markdown("---")
        st.markdown("## ⚙️ Settings")
        
        # Model selection
        available_models = get_available_models()
        
        # Handle empty available_models list
        if not available_models:
            available_models = ["No models available"]
            
        # Determine the index of the model in the dropdown
        if user_prefs.get("model") in available_models:
            model_index = available_models.index(user_prefs.get("model"))
        else:
            model_index = 0  # Default to first available model
            
        selected_model = st.selectbox(
            "Model",
            available_models,
            index=model_index,
            key="model_select"
        )
        
        if user_prefs.get("model") != selected_model:
            user_prefs["model"] = selected_model
            print(f"[DEBUG] sidebar: user={user}, selected_model={selected_model}")
            save_user_preference(user, "model", selected_model)

        # Draft model selection
        draft_models = ["None"] + available_models
        
        # Determine the index of the draft model in the dropdown
        if user_prefs.get("draft_model") in draft_models:
            draft_index = draft_models.index(user_prefs.get("draft_model"))
        else:
            draft_index = 0  # Default to "None"
            
        draft_model = st.selectbox(
            "Draft Model (Optional)",
            draft_models,
            index=draft_index,
            key="draft_model_select"
        )
        
        if user_prefs.get("draft_model") != draft_model:
            user_prefs["draft_model"] = draft_model
            save_user_preference(user, "draft_model", draft_model)
            
        # RAG endpoint
        rag_endpoints = ["Local Vector DB", "External RAG API"]
        
        # Determine the index of the RAG endpoint in the dropdown
        if user_prefs.get("rag_endpoint") in rag_endpoints:
            rag_index = rag_endpoints.index(user_prefs.get("rag_endpoint"))
        else:
            rag_index = 0  # Default to first option
            
        selected_rag = st.selectbox(
            "RAG Endpoint",
            rag_endpoints,
            index=rag_index,
            key="rag_endpoint"
        )
        
        if user_prefs.get("rag_endpoint") != selected_rag:
            user_prefs["rag_endpoint"] = selected_rag
            save_user_preference(user, "rag_endpoint", selected_rag)

        # DuckDuckGo fallback toggle
        fallback_default = user_prefs.get("duckduckgo_fallback", True)
        duckduckgo_fallback = st.checkbox(
            "Use DuckDuckGo as fallback for web search",
            value=fallback_default,
            help="If enabled, will use DuckDuckGo when main RAG returns no results."
        )
        if user_prefs.get("duckduckgo_fallback") != duckduckgo_fallback:
            user_prefs["duckduckgo_fallback"] = duckduckgo_fallback
            save_user_preference(user, "duckduckgo_fallback", duckduckgo_fallback)

        # LangGraph Workflow Toggle
        try:
            from agent.core.core import LANG_FAMILY_AVAILABLE
            if LANG_FAMILY_AVAILABLE:
                langgraph_default = user_prefs.get("use_langgraph_workflow", False)
                use_langgraph = st.checkbox(
                    "🔄 Use LangGraph Workflow (V2)",
                    value=langgraph_default,
                    help="Enable enhanced Plan->Code->Test->Reflect workflow with visualization"
                )
                if user_prefs.get("use_langgraph_workflow") != use_langgraph:
                    user_prefs["use_langgraph_workflow"] = use_langgraph
                    save_user_preference(user, "use_langgraph_workflow", use_langgraph)
                
                st.session_state["use_langgraph_workflow"] = use_langgraph
                
                if use_langgraph:
                    st.info("💡 LangGraph V2 workflow enabled")
            else:
                st.session_state["use_langgraph_workflow"] = False
        except ImportError:
            st.session_state["use_langgraph_workflow"] = False

        # Reasoning display preference
        reasoning_display_options = ["Expandable", "Inline", "Hidden"]
        
        # Determine the index of the reasoning display option in the dropdown
        default_reasoning = reasoning_display_options[0]
        selected_option = user_prefs.get("reasoning_display", default_reasoning)
        
        if selected_option in reasoning_display_options:
            reasoning_index = reasoning_display_options.index(selected_option)
        else:
            reasoning_index = 0  # Default to first option
            
        selected_reasoning_display = st.selectbox(
            "Reasoning Display",
            reasoning_display_options,
            index=reasoning_index,
            key="reasoning_display"
        )
        
        if user_prefs.get("reasoning_display") != selected_reasoning_display:
            user_prefs["reasoning_display"] = selected_reasoning_display
            save_user_preference(user, "reasoning_display", selected_reasoning_display)
            
        # LangChain API Key input
        langchain_api_key = user_prefs.get("langchain_api_key", "")
        new_langchain_api_key = st.text_input(
            "LangChain API Key",
            value=langchain_api_key,
            type="password",
            help="Paste your LangChain API key here."
        )
        if new_langchain_api_key != langchain_api_key:
            user_prefs["langchain_api_key"] = new_langchain_api_key
            save_user_preference(user, "langchain_api_key", new_langchain_api_key)

        # V2 LangGraph Architecture Toggle
        st.markdown("---")
        st.markdown("#### 🚀 V2 Architecture")
        
        use_langgraph_v2 = user_prefs.get("use_langgraph_v2", True)
        new_use_langgraph_v2 = st.checkbox(
            "Enable LangGraph V2",
            value=use_langgraph_v2,
            help="Use the new LangGraph-based agent architecture with cyclical reasoning workflow"
        )
        
        if new_use_langgraph_v2 != use_langgraph_v2:
            user_prefs["use_langgraph_v2"] = new_use_langgraph_v2
            save_user_preference(user, "use_langgraph_v2", new_use_langgraph_v2)
            st.session_state["use_langgraph_v2"] = new_use_langgraph_v2
            if new_use_langgraph_v2:
                st.success("✅ V2 LangGraph architecture enabled!")
            else:
                st.info("ℹ️ Using V1 compatibility mode")
        
        # Show V2 status indicator
        if new_use_langgraph_v2:
            try:
                from agent.core.langgraph_agent import LANGGRAPH_AVAILABLE
                if LANGGRAPH_AVAILABLE:
                    st.success("🟢 V2 LangGraph: Available")
                else:
                    st.warning("🟡 V2 LangGraph: Dependencies missing")
                    st.caption("Run: pip install langgraph langchain")
            except ImportError:
                st.error("🔴 V2 LangGraph: Not installed")
        else:
            st.info("🔵 V1 Compatibility Mode")
        
        # V2 Backend status (if enabled)
        if new_use_langgraph_v2:
            if st.button("🔧 Start V2 Backend"):
                st.info("V2 Backend can be started with: python scripts/start_v2_backend.py")
                st.code("cd /path/to/jarvis && python scripts/start_v2_backend.py --reload")
        
        st.session_state["use_langgraph_v2"] = new_use_langgraph_v2

        # Personal data backup/restore for all users
        st.markdown("---")
        st.markdown("## 💾 Data Management")
        
        # Backup current user data
        if st.button("📤 Backup My Data"):
            backup_path = backup_user_data(user)
            if backup_path:
                st.success(f"Your data has been backed up to: {backup_path}")
            else:
                st.error("Failed to create backup")
        
        # Import user data
        uploaded_file = st.file_uploader("Import Personal Backup:", type=["zip"])
        col1, col2 = st.columns(2)
        with col1:
            overwrite = st.checkbox("Overwrite existing data", value=False)
        
        with col2:
            if uploaded_file is not None:
                if st.button("📥 Restore My Data"):
                    try:
                        # Save the uploaded file temporarily
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_path = tmp_file.name
                        
                        # Import the data
                        result = import_user_data(temp_path, overwrite)
                        
                        # Remove temp file
                        os.unlink(temp_path)
                        
                        if isinstance(result, dict) and "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success(f"Successfully restored your data")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error restoring data: {e}")
        
        # Admin section for admins
        if st.session_state.get("is_admin", False):
            st.markdown("---")
            st.markdown("## 🔧 Admin Tools")
            
            # System-wide backup and restore
            st.write("### System Backup & Restore")
            
            if st.button("📤 Backup All Users"):
                backup_file = backup_all_user_data()
                st.success(f"All system data backed up to {backup_file}")
                
            uploaded_json = st.file_uploader("Import System Backup:", type=["json"])
            if uploaded_json is not None:
                if st.button("📥 Restore System Data"):
                    try:
                        result = import_user_data_from_json(uploaded_json)
                        st.success(f"Restored {result.get('preferences', 0)} preferences and {result.get('settings', 0)} settings")
                    except Exception as e:
                        st.error(f"Error restoring data: {e}")
                        
            # System settings
            st.write("### System Settings")
            system_settings = get_user_settings(username="admin")  # Using admin account for system settings
            
            max_tokens = st.number_input(
                "Max Response Tokens", 
                min_value=100,
                max_value=32000,
                value=int(system_settings.get("max_tokens", 4000))
            )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=float(system_settings.get("temperature", 0.7)),
                step=0.1
            )
            
            if st.button("Save System Settings"):
                settings = {
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                save_user_settings(settings)
                st.success("System settings saved")
                
        # Logout button at bottom
        st.markdown("---")
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
        # Display version
        st.markdown("---")
        st.markdown("##### Jarvis AI v2.5.0")
        
        return user_prefs
