"""
JetBrains IDE Integration Module
Provides integration with JetBrains IDEs (PyCharm, IntelliJ IDEA, etc.)
through command-line tools and HTTP API when available.
"""
import os
import subprocess
import json
import time
import psutil
from typing import List, Dict, Any, Optional


class JetBrainsIntegration:
    def __init__(self, ide_type: str = 'pycharm'):
        """
        Initialize JetBrains IDE integration.
        
        Args:
            ide_type: Type of IDE ('pycharm', 'idea', 'webstorm', 'phpstorm', etc.)
        """
        self.ide_type = ide_type.lower()
        self.ide_executables = {
            'pycharm': ['pycharm', 'pycharm64.exe', 'pycharm.exe', 'charm'],
            'idea': ['idea', 'idea64.exe', 'idea.exe'],
            'webstorm': ['webstorm', 'webstorm64.exe', 'webstorm.exe'],
            'phpstorm': ['phpstorm', 'phpstorm64.exe', 'phpstorm.exe'],
            'clion': ['clion', 'clion64.exe', 'clion.exe'],
            'goland': ['goland', 'goland64.exe', 'goland.exe'],
            'rider': ['rider', 'rider64.exe', 'rider.exe']
        }
        self.ide_path = self._find_ide_executable()
    
    def _find_ide_executable(self) -> Optional[str]:
        """Find the IDE executable in system PATH."""
        possible_executables = self.ide_executables.get(self.ide_type, [])
        
        for executable in possible_executables:
            try:
                # Check if executable exists in PATH
                result = subprocess.run(['which', executable], capture_output=True, text=True)
                if result.returncode == 0:
                    return executable
                
                # On Windows, try 'where' command
                result = subprocess.run(['where', executable], capture_output=True, text=True)
                if result.returncode == 0:
                    return executable.split('\n')[0].strip()
                    
            except FileNotFoundError:
                continue
        
        # Try common installation paths
        common_paths = self._get_common_install_paths()
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _get_common_install_paths(self) -> List[str]:
        """Get common installation paths for the IDE."""
        paths = []
        
        if os.name == 'nt':  # Windows
            program_files = [
                os.environ.get('PROGRAMFILES', r'C:\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')
            ]
            
            for pf in program_files:
                if self.ide_type == 'pycharm':
                    paths.extend([
                        os.path.join(pf, 'JetBrains', 'PyCharm Community Edition*', 'bin', 'pycharm64.exe'),
                        os.path.join(pf, 'JetBrains', 'PyCharm Professional*', 'bin', 'pycharm64.exe')
                    ])
                elif self.ide_type == 'idea':
                    paths.extend([
                        os.path.join(pf, 'JetBrains', 'IntelliJ IDEA Community Edition*', 'bin', 'idea64.exe'),
                        os.path.join(pf, 'JetBrains', 'IntelliJ IDEA*', 'bin', 'idea64.exe')
                    ])
        
        elif os.name == 'posix':  # Linux/macOS
            if self.ide_type == 'pycharm':
                paths.extend([
                    '/usr/local/bin/pycharm',
                    '/opt/pycharm/bin/pycharm.sh',
                    '/snap/bin/pycharm-community',
                    '/Applications/PyCharm.app/Contents/MacOS/pycharm'
                ])
            elif self.ide_type == 'idea':
                paths.extend([
                    '/usr/local/bin/idea',
                    '/opt/idea/bin/idea.sh',
                    '/snap/bin/intellij-idea-community',
                    '/Applications/IntelliJ IDEA.app/Contents/MacOS/idea'
                ])
        
        return [path for path in paths if os.path.exists(path)]
    
    def is_ide_running(self) -> bool:
        """Check if the IDE is currently running."""
        ide_processes = {
            'pycharm': ['pycharm', 'pycharm64', 'pycharm.exe'],
            'idea': ['idea', 'idea64', 'java'],  # IntelliJ runs as java process
            'webstorm': ['webstorm', 'webstorm64'],
            'phpstorm': ['phpstorm', 'phpstorm64'],
            'clion': ['clion', 'clion64'],
            'goland': ['goland', 'goland64'],
            'rider': ['rider', 'rider64']
        }
        
        process_names = ide_processes.get(self.ide_type, [])
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                for name in process_names:
                    if name in proc_name or (name == 'java' and self.ide_type in cmdline):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def open_file(self, file_path: str, line_number: int = None) -> Dict[str, Any]:
        """
        Open a file in the IDE.
        
        Args:
            file_path: Path to the file to open
            line_number: Optional line number to navigate to
        
        Returns:
            Operation result
        """
        if not self.ide_path:
            return {"error": f"{self.ide_type} executable not found"}
        
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Convert to absolute path
        file_path = os.path.abspath(file_path)
        
        # Build command
        cmd = [self.ide_path]
        
        if line_number:
            # JetBrains IDEs support --line parameter
            cmd.extend(['--line', str(line_number)])
        
        cmd.append(file_path)
        
        try:
            # Run command in background
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return {
                "success": True,
                "message": f"Opened {file_path} in {self.ide_type}",
                "file_path": file_path,
                "line_number": line_number
            }
        except Exception as e:
            return {"error": f"Failed to open file: {str(e)}"}
    
    def open_project(self, project_path: str) -> Dict[str, Any]:
        """
        Open a project in the IDE.
        
        Args:
            project_path: Path to the project directory
        
        Returns:
            Operation result
        """
        if not self.ide_path:
            return {"error": f"{self.ide_type} executable not found"}
        
        if not os.path.exists(project_path):
            return {"error": f"Project path not found: {project_path}"}
        
        if not os.path.isdir(project_path):
            return {"error": f"Project path is not a directory: {project_path}"}
        
        # Convert to absolute path
        project_path = os.path.abspath(project_path)
        
        try:
            # Run command in background
            subprocess.Popen([self.ide_path, project_path], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return {
                "success": True,
                "message": f"Opened project {project_path} in {self.ide_type}",
                "project_path": project_path
            }
        except Exception as e:
            return {"error": f"Failed to open project: {str(e)}"}
    
    def create_new_file(self, file_path: str, content: str = '', 
                       open_after_creation: bool = True) -> Dict[str, Any]:
        """
        Create a new file and optionally open it in the IDE.
        
        Args:
            file_path: Path for the new file
            content: Initial file content
            open_after_creation: Whether to open the file after creation
        
        Returns:
            Operation result
        """
        try:
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # Create file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "success": True,
                "message": f"Created file {file_path}",
                "file_path": file_path
            }
            
            if open_after_creation:
                open_result = self.open_file(file_path)
                if "error" in open_result:
                    result["warning"] = f"File created but failed to open: {open_result['error']}"
                else:
                    result["message"] += f" and opened in {self.ide_type}"
            
            return result
            
        except Exception as e:
            return {"error": f"Failed to create file: {str(e)}"}
    
    def run_ide_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Run IDE-specific command.
        
        Args:
            command: Command to run
            args: Command arguments
        
        Returns:
            Command result
        """
        if not self.ide_path:
            return {"error": f"{self.ide_type} executable not found"}
        
        cmd = [self.ide_path]
        
        # Add command-line options based on IDE type and command
        if command == 'format':
            # Code formatting command
            if args:
                cmd.extend(['format'] + args)
            else:
                return {"error": "Format command requires file paths"}
        elif command == 'inspect':
            # Code inspection command
            if args:
                cmd.extend(['inspect'] + args)
            else:
                return {"error": "Inspect command requires file paths"}
        elif command == 'diff':
            # Diff command
            if args and len(args) >= 2:
                cmd.extend(['diff'] + args[:2])
            else:
                return {"error": "Diff command requires two file paths"}
        else:
            return {"error": f"Unsupported command: {command}"}
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Command failed: {str(e)}"}
    
    def get_ide_info(self) -> Dict[str, Any]:
        """Get IDE information and status."""
        return {
            "ide_type": self.ide_type,
            "ide_path": self.ide_path,
            "is_installed": self.ide_path is not None,
            "is_running": self.is_ide_running(),
            "supported_commands": ["open_file", "open_project", "create_new_file", "format", "inspect", "diff"]
        }
    
    def find_ide_config_dir(self) -> Optional[str]:
        """Find IDE configuration directory."""
        config_dirs = {
            'pycharm': [
                os.path.expanduser('~/.PyCharm*'),
                os.path.expanduser('~/Library/Application Support/JetBrains/PyCharm*'),
                os.path.expanduser('~/AppData/Roaming/JetBrains/PyCharm*')
            ],
            'idea': [
                os.path.expanduser('~/.IntelliJIdea*'),
                os.path.expanduser('~/Library/Application Support/JetBrains/IntelliJIdea*'),
                os.path.expanduser('~/AppData/Roaming/JetBrains/IntelliJIdea*')
            ]
        }
        
        possible_dirs = config_dirs.get(self.ide_type, [])
        
        import glob
        for pattern in possible_dirs:
            matches = glob.glob(pattern)
            if matches:
                return sorted(matches)[-1]  # Return the latest version
        
        return None


def parse_ide_command(command: str) -> Dict[str, Any]:
    """
    Parse natural language IDE command.
    
    Args:
        command: Natural language command
    
    Returns:
        Parsed command information
    """
    command_lower = command.lower().strip()
    
    # Extract IDE type
    ide_type = 'pycharm'  # default
    if 'intellij' in command_lower or 'idea' in command_lower:
        ide_type = 'idea'
    elif 'webstorm' in command_lower:
        ide_type = 'webstorm'
    elif 'phpstorm' in command_lower:
        ide_type = 'phpstorm'
    elif 'clion' in command_lower:
        ide_type = 'clion'
    elif 'goland' in command_lower:
        ide_type = 'goland'
    elif 'rider' in command_lower:
        ide_type = 'rider'
    
    # Parse action and parameters
    if 'open in' in command_lower:
        # Extract file path
        parts = command.split()
        try:
            # Find 'in' keyword and get path after it
            in_index = [i for i, word in enumerate(parts) if word.lower() == 'in'][0]
            if in_index + 2 < len(parts):  # 'in pycharm <path>'
                path = ' '.join(parts[in_index + 2:])
            else:
                return {"error": "No file path specified"}
        except (IndexError, ValueError):
            return {"error": "Invalid command format"}
        
        # Check if line number is specified
        line_number = None
        if ':' in path and path.split(':')[-1].isdigit():
            path_parts = path.rsplit(':', 1)
            path = path_parts[0]
            line_number = int(path_parts[1])
        
        return {
            "action": "open_file",
            "ide_type": ide_type,
            "file_path": path,
            "line_number": line_number
        }
    
    elif 'create' in command_lower and 'file' in command_lower:
        # Extract file path
        parts = command.split()
        try:
            file_index = [i for i, word in enumerate(parts) if word.lower() == 'file'][0]
            if file_index + 1 < len(parts):
                path = ' '.join(parts[file_index + 1:])
            else:
                return {"error": "No file path specified"}
        except (IndexError, ValueError):
            return {"error": "Invalid command format"}
        
        return {
            "action": "create_file",
            "ide_type": ide_type,
            "file_path": path
        }
    
    elif 'open project' in command_lower:
        # Extract project path
        project_index = command_lower.find('project')
        if project_index != -1:
            path_part = command[project_index + 7:].strip()
            if path_part:
                return {
                    "action": "open_project",
                    "ide_type": ide_type,
                    "project_path": path_part
                }
        
        return {"error": "No project path specified"}
    
    else:
        return {"error": f"Unsupported IDE command: {command}"}


def execute_ide_command(command: str) -> Dict[str, Any]:
    """
    Execute IDE command based on natural language input.
    
    Args:
        command: Natural language IDE command
    
    Returns:
        Execution result
    """
    parsed = parse_ide_command(command)
    
    if "error" in parsed:
        return parsed
    
    ide = JetBrainsIntegration(parsed["ide_type"])
    
    if parsed["action"] == "open_file":
        return ide.open_file(parsed["file_path"], parsed.get("line_number"))
    elif parsed["action"] == "create_file":
        return ide.create_new_file(parsed["file_path"])
    elif parsed["action"] == "open_project":
        return ide.open_project(parsed["project_path"])
    else:
        return {"error": f"Unsupported action: {parsed['action']}"}


def get_available_ides() -> Dict[str, Any]:
    """Get information about available JetBrains IDEs."""
    ide_types = ['pycharm', 'idea', 'webstorm', 'phpstorm', 'clion', 'goland', 'rider']
    available = {}
    
    for ide_type in ide_types:
        ide = JetBrainsIntegration(ide_type)
        available[ide_type] = ide.get_ide_info()
    
    return available