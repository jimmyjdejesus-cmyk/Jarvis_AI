# Conflict Resolution and Dependency Fix TODO

## Files to Fix
- [x] jarvis/__init__.py - Remove duplicates, fix syntax errors
- [x] jarvis/dynamic_agents/default_tools.py - Resolve merge conflict, add missing imports
- [x] jarvis/persistence/session.py - Fix merge conflict and indentation
- [x] jarvis/agents/critics/red_team.py - Remove merge artifacts
- [x] jarvis/orchestration/orchestrator.py - Check import issues

## Progress
- [x] Created TODO.md to track progress
- [x] Fixed jarvis/__init__.py - Cleaned up duplicates, fixed syntax, organized imports
- [x] Fixed jarvis/dynamic_agents/default_tools.py - Merged both versions with Ollama support optional
- [x] Fixed jarvis/persistence/session.py - Fixed indentation and merged mission plan methods
- [x] Fixed jarvis/agents/critics/red_team.py - Cleaned up and added proper initialization
- [x] Fixed jarvis/orchestration/orchestrator.py - Added missing imports, removed duplicates
- [x] All Python syntax errors resolved
- [x] All merge conflicts resolved

## Summary of Changes

### 1. **jarvis/__init__.py**: 
   - Removed all duplicate code blocks (was repeated 3+ times)
   - Fixed incomplete except statements (changed from `except Exception:` to `except ImportError:`)
   - Organized imports properly with error handling
   - Fixed function definitions and removed duplicates
   - Added proper type hints for Python 3.10+ compatibility

### 2. **jarvis/dynamic_agents/default_tools.py**:
   - Merged both simple and Ollama-based implementations intelligently
   - Made Ollama optional via USE_OLLAMA environment variable
   - Added missing imports (os, requests)
   - Fixed incomplete function definitions and try-except blocks
   - Provides fallback logic when Ollama is not available

### 3. **jarvis/persistence/session.py**:
   - Fixed indentation issues throughout the file
   - Properly merged mission plan methods (save_mission_plan, load_mission_plan)
   - Cleaned up imports and added proper type hints
   - Removed duplicate method definitions

### 4. **jarvis/agents/critics/red_team.py**:
   - Removed all merge conflict markers
   - Fixed class initialization with proper model parameter
   - Made mcp_client optional with fallback behavior
   - Cleaned up return statements and error handling
   - Added proper __all__ export

### 5. **jarvis/orchestration/orchestrator.py**:
   - Added graceful handling for missing imports (yaml, langgraph)
   - Removed duplicate method definitions
   - Added missing coordinate_specialists method
   - Fixed _analyze_request method implementation
   - Added proper error handling for missing dependencies

## Dependency Notes
The following optional dependencies may need to be installed:
- `langgraph` - Required for DynamicOrchestrator (will raise ImportError if used without it)
- `yaml` - Optional, used for configuration parsing
- `requests` - Required if using Ollama integration in default_tools.py

## Testing Recommendations
1. Test imports: `python -c "import jarvis"`
2. Check for any remaining syntax errors
3. Verify Ollama integration works when USE_OLLAMA=true
4. Test specialist orchestration if dependencies are available
