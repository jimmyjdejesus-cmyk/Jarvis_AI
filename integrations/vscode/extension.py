"""VS Code Integration for Jarvis AI Coding Assistant.
Provides commands and API endpoints for IDE integration."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import asyncio

try:
    import websockets
    WebSocketServerProtocol = websockets.WebSocketServerProtocol
except ImportError:  # pragma: no cover - handled at runtime
    websockets = None
    from typing import Any as WebSocketServerProtocol

# Add the repository root to path to import jarvis
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from jarvis.tools.repository_indexer import RepositoryIndexer


def _get_coding_agent(workspace: Optional[str] = None):
    """Lazily import Jarvis and return a coding agent."""
    import jarvis  # local import to avoid heavy dependencies at module load

    base_agent = jarvis.get_jarvis_agent()
    return jarvis.get_coding_agent(base_agent, workspace) if workspace else jarvis.get_coding_agent(base_agent)


def get_repository_indexer(workspace: str) -> RepositoryIndexer:
    """Create and build a :class:`RepositoryIndexer` for a workspace."""
    path = str(Path(workspace).resolve())
    indexer = RepositoryIndexer(path)
    indexer.build_index(force_rebuild=True)
    return indexer

def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze a single file"""
    try:
        coding_agent = _get_coding_agent(str(Path(file_path).parent))

        result = coding_agent.analyze_file_content(file_path)
        
        return {
            "success": True,
            "analysis": result,
            "file": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file": file_path
        }

def review_code(file_path: str, language: str = None) -> Dict[str, Any]:
    """Review code in a file"""
    try:
        path = Path(file_path)
        if not language:
            language = get_language_from_file(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        coding_agent = _get_coding_agent()

        review = coding_agent.code_review(code, language, f"File: {path.name}")
        
        return {
            "success": True,
            "review": review,
            "file": file_path,
            "language": language
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file": file_path
        }

def generate_tests(file_path: str, language: str = None) -> Dict[str, Any]:
    """Generate tests for a file"""
    try:
        path = Path(file_path)
        if not language:
            language = get_language_from_file(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        coding_agent = _get_coding_agent()

        tests = coding_agent.create_tests(code, language)
        
        return {
            "success": True,
            "tests": tests,
            "file": file_path,
            "language": language
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file": file_path
        }

def explain_code_selection(code: str, language: str = "python", workspace: Optional[str] = None) -> Dict[str, Any]:
    """Explain selected code and surface related files."""
    try:
        coding_agent = _get_coding_agent()

        explanation = coding_agent.explain_code(code, language)
        suggestions: List[Dict[str, Any]] = []
        if workspace:
            indexer = get_repository_indexer(workspace)
            suggestions = indexer.search(code)

        return {
            "success": True,
            "explanation": explanation,
            "language": language,
            "suggestions": suggestions,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def debug_error(error_message: str, code: str = "", language: str = "python", workspace: Optional[str] = None) -> Dict[str, Any]:
    """Debug an error and suggest related files."""
    try:
        coding_agent = _get_coding_agent()

        debug_help = coding_agent.debug_assistance(error_message, code, language)
        related: List[Dict[str, Any]] = []
        if workspace:
            indexer = get_repository_indexer(workspace)
            related = indexer.search(error_message)

        return {
            "success": True,
            "debug_help": debug_help,
            "language": language,
            "related_files": related,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def analyze_workspace(workspace_path: str) -> Dict[str, Any]:
    """Analyze entire workspace"""
    try:
        coding_agent = _get_coding_agent(workspace_path)

        analysis = coding_agent.analyze_codebase(workspace_path)
        # ensure repository index is built for subsequent suggestions
        get_repository_indexer(workspace_path)

        return {
            "success": True,
            "analysis": analysis,
            "workspace": workspace_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "workspace": workspace_path
        }


async def _ws_handler(websocket: WebSocketServerProtocol):
    """Handle incoming websocket messages"""
    async for message in websocket:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send(json.dumps({"success": False, "error": "Invalid JSON format in request"}))
            continue

        command = data.get("command")
        response: Dict[str, Any]
        if command == "inline-suggestion":
            code = data.get("code", "")
            language = data.get("language", "python")
            workspace = data.get("workspace")
            response = explain_code_selection(code, language, workspace)
        elif command == "stream-context":
            workspace = data.get("workspace", "")
            response = analyze_workspace(workspace)
        elif command == "debug-error":
            err = data.get("error", "")
            code = data.get("code", "")
            language = data.get("language", "python")
            workspace = data.get("workspace")
            response = debug_error(err, code, language, workspace)
        else:
            response = {"success": False, "error": f"Unknown command: {command}"}

        if "id" in data:
            response["id"] = data["id"]
        await websocket.send(json.dumps(response))


def run_websocket_server(host: str = "localhost", port: int = 8765) -> None:
    """Start a websocket server for VS Code extension"""
    if websockets is None:
        raise RuntimeError("websockets package is required to run the server")
    start_server = websockets.serve(_ws_handler, host, port)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    async def _start():
        async with websockets.serve(_ws_handler, host, port):
            await asyncio.Future()  # run forever
    asyncio.run(_start())

def get_language_from_file(file_path: str) -> str:
    """Determine language from file extension"""
    ext = Path(file_path).suffix.lower()
    mapping = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin'
    }
    return mapping.get(ext, 'text')

def main():
    """Command line interface for VS Code integration"""
    parser = argparse.ArgumentParser(description="Jarvis AI Coding Assistant CLI")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("--file", help="File path")
    parser.add_argument("--workspace", help="Workspace path")
    parser.add_argument("--code", help="Code content")
    parser.add_argument("--error", help="Error message")
    parser.add_argument("--language", help="Programming language")
    parser.add_argument("--output", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--server", action="store_true", help="Run as websocket server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--client", choices=[
        "analyze-file", "review-code", "generate-tests",
        "explain-code", "debug-error", "analyze-workspace"
    ], help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.server:
        run_websocket_server(args.host, args.port)
        return

    command = args.command or args.client
    result = None

    if command == "analyze-file" and args.file:
        result = analyze_file(args.file)
    elif command == "review-code" and args.file:
        result = review_code(args.file, args.language)
    elif command == "generate-tests" and args.file:
        result = generate_tests(args.file, args.language)
    elif command == "explain-code" and args.code:
        language = args.language or "python"
        result = explain_code_selection(args.code, language, args.workspace)
    elif command == "debug-error" and args.error:
        result = debug_error(args.error, args.code or "", args.language or "python", args.workspace)
    elif command == "analyze-workspace" and args.workspace:
        result = analyze_workspace(args.workspace)
    else:
        print("Invalid command or missing required arguments")
        parser.print_help()
        return

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            for key, value in result.items():
                if key not in ["success"]:
                    print(f"{key.title()}: {value}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
