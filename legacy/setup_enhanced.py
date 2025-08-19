"""
Enhanced Setup and Installation Script for Jarvis AI
Provides comprehensive system setup, dependency checking, and installation validation.
"""

import os
import sys
import subprocess
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import shutil
import platform

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from agent.core.error_handling import get_logger, robust_operation
    from agent.core.config_manager import get_config_manager, JarvisConfig
    from agent.core.testing_framework import run_quick_tests
except ImportError:
    # Fallback for basic logging if our modules aren't available yet
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def get_logger():
        return type('Logger', (), {'logger': logger})()
    
    def robust_operation(operation_name=None):
        def decorator(func):
            return func
        return decorator


class JarvisInstaller:
    """Comprehensive Jarvis AI installation and setup manager."""
    
    def __init__(self):
        self.logger = get_logger()
        self.project_root = project_root
        self.platform = platform.system().lower()
        self.python_version = sys.version_info
        self.setup_results = {}
    
    @robust_operation(operation_name="full_setup")
    def setup_jarvis(self, skip_optional: bool = False) -> Dict[str, Any]:
        """Run complete Jarvis AI setup process."""
        self.logger.logger.info("🚀 Starting Jarvis AI setup...")
        
        setup_steps = [
            ("System Requirements Check", self._check_system_requirements),
            ("Python Environment Setup", self._setup_python_environment),
            ("Directory Structure Creation", self._create_directory_structure),
            ("Dependencies Installation", self._install_dependencies),
            ("Configuration Setup", self._setup_configuration),
            ("Database Initialization", self._initialize_database),
            ("Service Dependencies Check", self._check_service_dependencies),
            ("Permissions Setup", self._setup_permissions),
            ("Quick Tests", self._run_initial_tests)
        ]
        
        if not skip_optional:
            setup_steps.extend([
                ("Optional Dependencies", self._install_optional_dependencies),
                ("External Service Setup", self._setup_external_services)
            ])
        
        total_steps = len(setup_steps)
        completed_steps = 0
        
        for step_name, step_function in setup_steps:
            try:
                self.logger.logger.info(f"📋 Step {completed_steps + 1}/{total_steps}: {step_name}")
                result = step_function()
                self.setup_results[step_name] = {"success": True, "details": result}
                completed_steps += 1
                self.logger.logger.info(f"✅ {step_name} completed successfully")
                
            except Exception as e:
                self.setup_results[step_name] = {"success": False, "error": str(e)}
                self.logger.logger.error(f"❌ {step_name} failed: {e}")
                
                # Ask user if they want to continue
                if self._should_continue_on_error(step_name):
                    completed_steps += 1
                    continue
                else:
                    break
        
        return self._generate_setup_report(completed_steps, total_steps)
    
    def _check_system_requirements(self) -> Dict[str, Any]:
        """Check if system meets minimum requirements."""
        requirements = {
            "python_version": self.python_version >= (3, 8),
            "platform_supported": self.platform in ['linux', 'darwin', 'windows'],
            "disk_space": self._check_disk_space(),
            "memory": self._check_memory(),
            "permissions": self._check_permissions()
        }
        
        # Critical checks
        if not requirements["python_version"]:
            raise Exception(f"Python 3.8+ required, found {self.python_version}")
        
        if not requirements["platform_supported"]:
            self.logger.logger.warning(f"Platform {self.platform} may not be fully supported")
        
        return requirements
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            import psutil
            disk = psutil.disk_usage(self.project_root)
            free_gb = disk.free / (1024**3)
            
            return {
                "free_space_gb": free_gb,
                "sufficient": free_gb >= 1.0  # Require at least 1GB
            }
        except ImportError:
            return {"free_space_gb": "unknown", "sufficient": True}
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check available memory."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            return {
                "available_memory_gb": available_gb,
                "sufficient": available_gb >= 2.0  # Require at least 2GB
            }
        except ImportError:
            return {"available_memory_gb": "unknown", "sufficient": True}
    
    def _check_permissions(self) -> Dict[str, Any]:
        """Check file system permissions."""
        test_file = os.path.join(self.project_root, ".permission_test")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return {"write_permission": True}
        except:
            return {"write_permission": False}
    
    def _setup_python_environment(self) -> Dict[str, Any]:
        """Set up Python environment and virtual environment if needed."""
        results = {
            "python_executable": sys.executable,
            "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            "virtual_env": None
        }
        
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        results["in_virtual_env"] = in_venv
        
        if not in_venv:
            self.logger.logger.warning("Not running in virtual environment. Consider using 'python -m venv venv'")
        
        # Upgrade pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            results["pip_upgraded"] = True
        except subprocess.CalledProcessError:
            results["pip_upgraded"] = False
            self.logger.logger.warning("Failed to upgrade pip")
        
        return results
    
    def _create_directory_structure(self) -> Dict[str, Any]:
        """Create necessary directory structure."""
        directories = [
            "data",
            "logs", 
            "plugins",
            "config",
            "database",
            "temp",
            "backups"
        ]
        
        created_dirs = []
        for directory in directories:
            dir_path = os.path.join(self.project_root, directory)
            try:
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(directory)
            except Exception as e:
                self.logger.logger.warning(f"Could not create directory {directory}: {e}")
        
        return {"created_directories": created_dirs}
    
    def _install_dependencies(self) -> Dict[str, Any]:
        """Install required Python dependencies."""
        # Core dependencies
        core_deps = [
            "streamlit>=1.30.0",
            "requests>=2.31.0", 
            "pyyaml",
            "psutil",
            "bcrypt",
            "cryptography"
        ]
        
        # Enhanced dependencies
        enhanced_deps = [
            "duckduckgo-search>=4.0.0",
            "plotly",
            "pytest",
            "playwright"
        ]
        
        results = {
            "core_dependencies": self._install_package_list(core_deps),
            "enhanced_dependencies": self._install_package_list(enhanced_deps)
        }
        
        return results
    
    def _install_package_list(self, packages: List[str]) -> Dict[str, bool]:
        """Install a list of packages and return success status for each."""
        results = {}
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True)
                results[package] = True
                self.logger.logger.info(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                results[package] = False
                self.logger.logger.warning(f"❌ Failed to install {package}: {e}")
        
        return results
    
    def _install_optional_dependencies(self) -> Dict[str, Any]:
        """Install optional dependencies that enhance functionality."""
        optional_deps = [
            "gitpython",  # For enhanced git operations
            "notebook",   # For Jupyter integration
            "matplotlib", # For additional plotting
            "pandas",     # For data analysis
            "numpy"       # For numerical operations
        ]
        
        return {"optional_dependencies": self._install_package_list(optional_deps)}
    
    def _setup_configuration(self) -> Dict[str, Any]:
        """Set up default configuration."""
        try:
            config_manager = get_config_manager()
            config = config_manager.load_config()
            
            # Update configuration with installation-specific settings
            config.debug_mode = True  # Enable debug mode initially
            config.data_directory = os.path.join(self.project_root, "data")
            config.logs_directory = os.path.join(self.project_root, "logs")
            config.plugins_directory = os.path.join(self.project_root, "plugins")
            
            # Set secure defaults
            import secrets
            if config.security.cookie_secret_key == "change_this_secret_key":
                config.security.cookie_secret_key = secrets.token_urlsafe(32)
            
            config_manager.save_config(config)
            
            return {
                "config_created": True,
                "config_path": config_manager.config_path,
                "secure_key_generated": True
            }
            
        except Exception as e:
            self.logger.logger.warning(f"Could not set up configuration: {e}")
            return {"config_created": False, "error": str(e)}
    
    def _initialize_database(self) -> Dict[str, Any]:
        """Initialize database if needed."""
        db_path = os.path.join(self.project_root, "database", "jarvis.db")
        
        try:
            # Check if database exists
            if os.path.exists(db_path):
                return {"database_exists": True, "path": db_path}
            
            # Try to initialize database (if we have the module)
            try:
                from database.user_management import init_database
                init_database()
                return {"database_initialized": True, "path": db_path}
            except ImportError:
                self.logger.logger.info("Database module not available, skipping database initialization")
                return {"database_skipped": True, "reason": "module_not_available"}
                
        except Exception as e:
            return {"database_error": True, "error": str(e)}
    
    def _check_service_dependencies(self) -> Dict[str, Any]:
        """Check external service dependencies."""
        services = {
            "ollama": self._check_ollama(),
            "git": self._check_git(),
            "node": self._check_node()
        }
        
        return services
    
    def _check_ollama(self) -> Dict[str, Any]:
        """Check if Ollama service is available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "available": True,
                    "models_count": len(models),
                    "models": [m.get("name", "unknown") for m in models[:5]]  # First 5 models
                }
            else:
                return {"available": False, "reason": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_git(self) -> Dict[str, Any]:
        """Check if Git is available."""
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {"available": True, "version": result.stdout.strip()}
            else:
                return {"available": False, "reason": "git command failed"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_node(self) -> Dict[str, Any]:
        """Check if Node.js is available (for some integrations)."""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {"available": True, "version": result.stdout.strip()}
            else:
                return {"available": False, "reason": "node command failed"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _setup_permissions(self) -> Dict[str, Any]:
        """Set up file permissions."""
        if self.platform != "windows":
            try:
                # Make shell scripts executable
                shell_scripts = ["launch.sh", "ide_launch.sh"]
                made_executable = []
                
                for script in shell_scripts:
                    script_path = os.path.join(self.project_root, script)
                    if os.path.exists(script_path):
                        os.chmod(script_path, 0o755)
                        made_executable.append(script)
                
                return {"executable_scripts": made_executable}
            except Exception as e:
                return {"permission_error": str(e)}
        
        return {"platform": "windows", "no_permission_changes": True}
    
    def _setup_external_services(self) -> Dict[str, Any]:
        """Set up external service integrations."""
        results = {}
        
        # GitHub integration setup
        github_token = os.getenv("GITHUB_TOKEN")
        results["github"] = {
            "token_available": github_token is not None,
            "configured": github_token is not None
        }
        
        # Notion integration setup
        notion_token = os.getenv("NOTION_TOKEN")
        results["notion"] = {
            "token_available": notion_token is not None,
            "configured": notion_token is not None
        }
        
        return results
    
    def _run_initial_tests(self) -> Dict[str, Any]:
        """Run initial tests to verify setup."""
        try:
            success = run_quick_tests()
            return {"tests_passed": success}
        except Exception as e:
            return {"tests_failed": True, "error": str(e)}
    
    def _should_continue_on_error(self, step_name: str) -> bool:
        """Determine if setup should continue after a step fails."""
        critical_steps = [
            "System Requirements Check",
            "Python Environment Setup", 
            "Dependencies Installation"
        ]
        
        if step_name in critical_steps:
            return False
        
        # For non-critical steps, continue by default
        return True
    
    def _generate_setup_report(self, completed_steps: int, total_steps: int) -> Dict[str, Any]:
        """Generate comprehensive setup report."""
        successful_steps = sum(1 for result in self.setup_results.values() if result["success"])
        failed_steps = [name for name, result in self.setup_results.items() if not result["success"]]
        
        report = {
            "timestamp": time.time(),
            "completion_status": {
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "completion_rate": completed_steps / total_steps,
                "success_rate": successful_steps / total_steps
            },
            "setup_results": self.setup_results,
            "failed_steps": failed_steps,
            "next_steps": self._generate_next_steps(failed_steps),
            "system_info": {
                "platform": self.platform,
                "python_version": f"{self.python_version.major}.{self.python_version.minor}",
                "project_root": self.project_root
            }
        }
        
        return report
    
    def _generate_next_steps(self, failed_steps: List[str]) -> List[str]:
        """Generate recommendations for next steps."""
        next_steps = []
        
        if not failed_steps:
            next_steps.extend([
                "🎉 Setup completed successfully!",
                "Run 'python app.py' to start Jarvis AI",
                "Check the documentation for usage instructions",
                "Consider setting up Ollama for local AI models"
            ])
        else:
            next_steps.append("⚠️ Some setup steps failed. Please address the following:")
            
            for step in failed_steps:
                if "Dependencies" in step:
                    next_steps.append("- Check internet connectivity and retry dependency installation")
                elif "Ollama" in step:
                    next_steps.append("- Install Ollama from https://ollama.ai/ for local AI models")
                elif "Database" in step:
                    next_steps.append("- Check database directory permissions")
                else:
                    next_steps.append(f"- Review and fix: {step}")
            
            next_steps.extend([
                "- Re-run setup after addressing issues",
                "- Check logs for detailed error information"
            ])
        
        return next_steps
    
    def generate_installation_script(self, platform: str = None) -> str:
        """Generate platform-specific installation script."""
        platform = platform or self.platform
        
        if platform == "linux" or platform == "darwin":
            return self._generate_unix_script()
        elif platform == "windows":
            return self._generate_windows_script()
        else:
            return "# Unsupported platform"
    
    def _generate_unix_script(self) -> str:
        """Generate Unix/Linux installation script."""
        return """#!/bin/bash
# Jarvis AI Installation Script for Unix/Linux

echo "🚀 Installing Jarvis AI..."

# Check Python version
python3 --version || { echo "Python 3 not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Jarvis AI
python setup_enhanced.py

echo "✅ Installation complete! Run 'source venv/bin/activate && python app.py' to start Jarvis AI"
"""
    
    def _generate_windows_script(self) -> str:
        """Generate Windows installation script."""
        return """@echo off
REM Jarvis AI Installation Script for Windows

echo 🚀 Installing Jarvis AI...

REM Check Python version
python --version || (
    echo Python not found. Please install Python 3.8+ from python.org
    exit /b 1
)

REM Create virtual environment
python -m venv venv
call venv\\Scripts\\activate.bat

REM Upgrade pip
pip install --upgrade pip

REM Install Jarvis AI
python setup_enhanced.py

echo ✅ Installation complete! Run 'venv\\Scripts\\activate.bat && python app.py' to start Jarvis AI
pause
"""


def main():
    """Main installation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jarvis AI Enhanced Setup")
    parser.add_argument("--skip-optional", action="store_true", 
                       help="Skip optional dependencies")
    parser.add_argument("--generate-script", choices=["linux", "darwin", "windows"],
                       help="Generate installation script for platform")
    parser.add_argument("--quick-test", action="store_true",
                       help="Run quick tests only")
    
    args = parser.parse_args()
    
    installer = JarvisInstaller()
    
    if args.generate_script:
        script = installer.generate_installation_script(args.generate_script)
        script_name = f"install_{args.generate_script}.{'sh' if args.generate_script != 'windows' else 'bat'}"
        with open(script_name, 'w') as f:
            f.write(script)
        print(f"Generated installation script: {script_name}")
        return
    
    if args.quick_test:
        try:
            success = run_quick_tests()
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"Quick tests failed: {e}")
            sys.exit(1)
    
    # Run full setup
    try:
        report = installer.setup_jarvis(skip_optional=args.skip_optional)
        
        print("\n" + "="*60)
        print("📊 JARVIS AI SETUP REPORT")
        print("="*60)
        
        status = report["completion_status"]
        print(f"✅ Completed: {status['completed_steps']}/{status['total_steps']} steps")
        print(f"🎯 Success Rate: {status['success_rate']:.1%}")
        
        if report["failed_steps"]:
            print(f"\n❌ Failed Steps: {', '.join(report['failed_steps'])}")
        
        print("\n📋 Next Steps:")
        for step in report["next_steps"]:
            print(f"   {step}")
        
        print("\n" + "="*60)
        
        # Save detailed report
        report_file = os.path.join(installer.project_root, "setup_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if status["success_rate"] > 0.8 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()