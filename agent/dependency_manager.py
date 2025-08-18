"""
Dependency Management Module
Provides automated dependency updates, security scanning, and management.
"""
import os
import json
import re
import subprocess
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta


class DependencyManager:
    def __init__(self, repository_path: str = None):
        self.repository_path = repository_path or os.getcwd()
        self.supported_files = {
            'python': ['requirements.txt', 'requirements-dev.txt', 'Pipfile', 'pyproject.toml', 'setup.py'],
            'javascript': ['package.json', 'package-lock.json', 'yarn.lock'],
            'java': ['pom.xml', 'build.gradle'],
            'csharp': ['*.csproj', 'packages.config'],
            'ruby': ['Gemfile', 'Gemfile.lock'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock']
        }
    
    def analyze_dependencies(self, project_type: str = None) -> Dict[str, Any]:
        """Analyze project dependencies and identify potential issues."""
        results = {
            "project_type": project_type,
            "dependency_files": [],
            "dependencies": {},
            "vulnerabilities": [],
            "outdated_packages": [],
            "license_issues": [],
            "suggestions": []
        }
        
        # Auto-detect project type if not provided
        if not project_type:
            project_type = self._detect_project_type()
            results["project_type"] = project_type
        
        # Find dependency files
        dependency_files = self._find_dependency_files(project_type)
        results["dependency_files"] = dependency_files
        
        if not dependency_files:
            results["suggestions"].append(f"No dependency files found for {project_type} project")
            return results
        
        try:
            # Parse dependencies
            for file_path in dependency_files:
                deps = self._parse_dependency_file(file_path, project_type)
                results["dependencies"][file_path] = deps
            
            # Check for vulnerabilities
            if project_type == 'python':
                results["vulnerabilities"] = self._check_python_vulnerabilities()
            elif project_type == 'javascript':
                results["vulnerabilities"] = self._check_npm_vulnerabilities()
            elif project_type == 'java':
                results["vulnerabilities"] = self._check_java_vulnerabilities()
            
            # Check for outdated packages
            results["outdated_packages"] = self._check_outdated_packages(project_type)
            
            # Check licenses
            results["license_issues"] = self._check_license_compatibility(project_type)
            
            # Generate suggestions
            results["suggestions"] = self._generate_dependency_suggestions(results)
            
            return results
            
        except Exception as e:
            results["error"] = f"Dependency analysis failed: {str(e)}"
            return results
    
    def _detect_project_type(self) -> str:
        """Auto-detect project type based on files present."""
        for project_type, files in self.supported_files.items():
            for file_pattern in files:
                if '*' in file_pattern:
                    # Handle glob patterns
                    import glob
                    matches = glob.glob(os.path.join(self.repository_path, file_pattern))
                    if matches:
                        return project_type
                else:
                    file_path = os.path.join(self.repository_path, file_pattern)
                    if os.path.exists(file_path):
                        return project_type
        
        return 'unknown'
    
    def _find_dependency_files(self, project_type: str) -> List[str]:
        """Find all dependency files for the given project type."""
        files = []
        
        if project_type in self.supported_files:
            for file_pattern in self.supported_files[project_type]:
                if '*' in file_pattern:
                    import glob
                    matches = glob.glob(os.path.join(self.repository_path, file_pattern))
                    files.extend(matches)
                else:
                    file_path = os.path.join(self.repository_path, file_pattern)
                    if os.path.exists(file_path):
                        files.append(file_path)
        
        return files
    
    def _parse_dependency_file(self, file_path: str, project_type: str) -> Dict[str, Any]:
        """Parse a dependency file and extract package information."""
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if project_type == 'python':
                return self._parse_python_dependencies(content, filename)
            elif project_type == 'javascript':
                return self._parse_javascript_dependencies(content, filename)
            elif project_type == 'java':
                return self._parse_java_dependencies(content, filename)
            elif project_type == 'go':
                return self._parse_go_dependencies(content, filename)
            elif project_type == 'rust':
                return self._parse_rust_dependencies(content, filename)
            else:
                return {"packages": [], "dev_packages": []}
                
        except Exception as e:
            return {"error": f"Failed to parse {filename}: {str(e)}"}
    
    def _parse_python_dependencies(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse Python dependency files."""
        packages = []
        dev_packages = []
        
        if filename.startswith('requirements'):
            # Parse requirements.txt format
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    package_info = self._parse_python_requirement(line)
                    if package_info:
                        if 'dev' in filename:
                            dev_packages.append(package_info)
                        else:
                            packages.append(package_info)
        
        elif filename == 'pyproject.toml':
            # Parse pyproject.toml
            try:
                import toml
                data = toml.loads(content)
                
                # Main dependencies
                if 'project' in data and 'dependencies' in data['project']:
                    for dep in data['project']['dependencies']:
                        package_info = self._parse_python_requirement(dep)
                        if package_info:
                            packages.append(package_info)
                
                # Optional dependencies
                if 'project' in data and 'optional-dependencies' in data['project']:
                    for group, deps in data['project']['optional-dependencies'].items():
                        for dep in deps:
                            package_info = self._parse_python_requirement(dep)
                            if package_info:
                                package_info['group'] = group
                                dev_packages.append(package_info)
                
            except ImportError:
                # Fallback parsing without toml library
                import re
                dependencies = re.findall(r'"([^"]+)"', content)
                for dep in dependencies:
                    package_info = self._parse_python_requirement(dep)
                    if package_info:
                        packages.append(package_info)
        
        elif filename == 'Pipfile':
            # Parse Pipfile format
            try:
                import toml
                data = toml.loads(content)
                
                if 'packages' in data:
                    for name, version in data['packages'].items():
                        packages.append({
                            "name": name,
                            "version": version if isinstance(version, str) else "*",
                            "type": "production"
                        })
                
                if 'dev-packages' in data:
                    for name, version in data['dev-packages'].items():
                        dev_packages.append({
                            "name": name,
                            "version": version if isinstance(version, str) else "*",
                            "type": "development"
                        })
                        
            except ImportError:
                pass  # Skip Pipfile parsing if toml not available
        
        return {
            "packages": packages,
            "dev_packages": dev_packages,
            "total_count": len(packages) + len(dev_packages)
        }
    
    def _parse_python_requirement(self, requirement: str) -> Optional[Dict[str, str]]:
        """Parse a single Python requirement string."""
        # Handle different requirement formats
        patterns = [
            r'^([a-zA-Z0-9_-]+)\s*([><=!]+)\s*([0-9.]+.*)',  # package>=1.0.0
            r'^([a-zA-Z0-9_-]+)\s*==\s*([0-9.]+.*)',          # package==1.0.0
            r'^([a-zA-Z0-9_-]+)\s*$'                          # package (no version)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, requirement.strip())
            if match:
                if len(match.groups()) >= 3:
                    return {
                        "name": match.group(1),
                        "operator": match.group(2),
                        "version": match.group(3),
                        "requirement": requirement
                    }
                elif len(match.groups()) == 2:
                    return {
                        "name": match.group(1),
                        "operator": "==",
                        "version": match.group(2),
                        "requirement": requirement
                    }
                else:
                    return {
                        "name": match.group(1),
                        "operator": "",
                        "version": "*",
                        "requirement": requirement
                    }
        
        return None
    
    def _parse_javascript_dependencies(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse JavaScript/Node.js dependency files."""
        packages = []
        dev_packages = []
        
        if filename == 'package.json':
            try:
                data = json.loads(content)
                
                # Production dependencies
                if 'dependencies' in data:
                    for name, version in data['dependencies'].items():
                        packages.append({
                            "name": name,
                            "version": version,
                            "type": "production"
                        })
                
                # Development dependencies
                if 'devDependencies' in data:
                    for name, version in data['devDependencies'].items():
                        dev_packages.append({
                            "name": name,
                            "version": version,
                            "type": "development"
                        })
                
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in package.json"}
        
        return {
            "packages": packages,
            "dev_packages": dev_packages,
            "total_count": len(packages) + len(dev_packages)
        }
    
    def _parse_java_dependencies(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse Java dependency files."""
        packages = []
        
        if filename == 'pom.xml':
            # Parse Maven POM file
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(content)
                
                # Find dependencies
                for dependency in root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency'):
                    group_id = dependency.find('{http://maven.apache.org/POM/4.0.0}groupId')
                    artifact_id = dependency.find('{http://maven.apache.org/POM/4.0.0}artifactId')
                    version = dependency.find('{http://maven.apache.org/POM/4.0.0}version')
                    
                    if group_id is not None and artifact_id is not None:
                        packages.append({
                            "name": f"{group_id.text}:{artifact_id.text}",
                            "version": version.text if version is not None else "unknown",
                            "group_id": group_id.text,
                            "artifact_id": artifact_id.text
                        })
                        
            except ET.ParseError:
                return {"error": "Invalid XML in pom.xml"}
        
        elif filename == 'build.gradle':
            # Parse Gradle build file (basic implementation)
            lines = content.split('\n')
            in_dependencies = False
            
            for line in lines:
                line = line.strip()
                if 'dependencies' in line and '{' in line:
                    in_dependencies = True
                elif in_dependencies and '}' in line:
                    in_dependencies = False
                elif in_dependencies:
                    # Look for dependency declarations
                    patterns = [
                        r"implementation\s+['\"]([^:]+):([^:]+):([^'\"]+)['\"]",
                        r"compile\s+['\"]([^:]+):([^:]+):([^'\"]+)['\"]"
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            packages.append({
                                "name": f"{match.group(1)}:{match.group(2)}",
                                "version": match.group(3),
                                "group_id": match.group(1),
                                "artifact_id": match.group(2)
                            })
        
        return {
            "packages": packages,
            "dev_packages": [],
            "total_count": len(packages)
        }
    
    def _parse_go_dependencies(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse Go dependency files."""
        packages = []
        
        if filename == 'go.mod':
            lines = content.split('\n')
            in_require = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('require'):
                    if '(' in line:
                        in_require = True
                    else:
                        # Single require
                        match = re.search(r'require\s+([^\s]+)\s+([^\s]+)', line)
                        if match:
                            packages.append({
                                "name": match.group(1),
                                "version": match.group(2)
                            })
                elif in_require and line == ')':
                    in_require = False
                elif in_require and line:
                    # Parse require block entry
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append({
                            "name": parts[0],
                            "version": parts[1]
                        })
        
        return {
            "packages": packages,
            "dev_packages": [],
            "total_count": len(packages)
        }
    
    def _parse_rust_dependencies(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse Rust dependency files."""
        packages = []
        dev_packages = []
        
        if filename == 'Cargo.toml':
            try:
                import toml
                data = toml.loads(content)
                
                # Production dependencies
                if 'dependencies' in data:
                    for name, version_info in data['dependencies'].items():
                        version = version_info if isinstance(version_info, str) else version_info.get('version', '*')
                        packages.append({
                            "name": name,
                            "version": version
                        })
                
                # Development dependencies
                if 'dev-dependencies' in data:
                    for name, version_info in data['dev-dependencies'].items():
                        version = version_info if isinstance(version_info, str) else version_info.get('version', '*')
                        dev_packages.append({
                            "name": name,
                            "version": version,
                            "type": "development"
                        })
                        
            except ImportError:
                pass  # Skip if toml not available
        
        return {
            "packages": packages,
            "dev_packages": dev_packages,
            "total_count": len(packages) + len(dev_packages)
        }
    
    def _check_python_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check Python packages for security vulnerabilities."""
        vulnerabilities = []
        
        try:
            # Try using safety package if available
            result = subprocess.run(['safety', 'check', '--json'], 
                                 capture_output=True, text=True, cwd=self.repository_path)
            
            if result.returncode == 0:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        vulnerabilities.append({
                            "package": vuln.get('package_name'),
                            "version": vuln.get('installed_version'),
                            "vulnerability_id": vuln.get('vulnerability_id'),
                            "advisory": vuln.get('advisory'),
                            "severity": "high"  # Safety doesn't provide severity
                        })
                except json.JSONDecodeError:
                    pass
            
        except FileNotFoundError:
            # Safety not installed, try pip-audit
            try:
                result = subprocess.run(['pip-audit', '--format=json'], 
                                     capture_output=True, text=True, cwd=self.repository_path)
                
                if result.returncode == 0:
                    try:
                        audit_data = json.loads(result.stdout)
                        for vuln in audit_data.get('vulnerabilities', []):
                            vulnerabilities.append({
                                "package": vuln.get('package'),
                                "version": vuln.get('installed_version'),
                                "vulnerability_id": vuln.get('id'),
                                "advisory": vuln.get('advisory'),
                                "severity": vuln.get('severity', 'unknown')
                            })
                    except json.JSONDecodeError:
                        pass
                        
            except FileNotFoundError:
                # Neither safety nor pip-audit available
                vulnerabilities.append({
                    "note": "Install 'safety' or 'pip-audit' for vulnerability scanning",
                    "install_command": "pip install safety"
                })
        
        return vulnerabilities
    
    def _check_npm_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check npm packages for security vulnerabilities."""
        vulnerabilities = []
        
        try:
            result = subprocess.run(['npm', 'audit', '--json'], 
                                 capture_output=True, text=True, cwd=self.repository_path)
            
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    
                    # Handle npm audit v6 and v7+ formats
                    if 'advisories' in audit_data:  # npm v6
                        for advisory in audit_data['advisories'].values():
                            vulnerabilities.append({
                                "package": advisory.get('module_name'),
                                "version": advisory.get('findings', [{}])[0].get('version'),
                                "vulnerability_id": advisory.get('id'),
                                "advisory": advisory.get('title'),
                                "severity": advisory.get('severity')
                            })
                    elif 'vulnerabilities' in audit_data:  # npm v7+
                        for pkg, vuln_info in audit_data['vulnerabilities'].items():
                            vulnerabilities.append({
                                "package": pkg,
                                "version": vuln_info.get('range'),
                                "vulnerability_id": str(vuln_info.get('via', [{}])[0].get('source')),
                                "advisory": vuln_info.get('title'),
                                "severity": vuln_info.get('severity')
                            })
                            
                except json.JSONDecodeError:
                    pass
                    
        except FileNotFoundError:
            vulnerabilities.append({
                "note": "npm not available for vulnerability scanning"
            })
        
        return vulnerabilities
    
    def _check_java_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check Java packages for security vulnerabilities."""
        vulnerabilities = []
        
        # Java vulnerability checking typically requires specialized tools
        # like OWASP Dependency Check or Snyk
        vulnerabilities.append({
            "note": "Java vulnerability scanning requires OWASP Dependency Check or similar tools",
            "suggestions": [
                "Install OWASP Dependency Check Maven/Gradle plugin",
                "Use Snyk for Java dependency scanning",
                "Configure GitHub Dependabot for automated scanning"
            ]
        })
        
        return vulnerabilities
    
    def _check_outdated_packages(self, project_type: str) -> List[Dict[str, Any]]:
        """Check for outdated packages."""
        outdated = []
        
        try:
            if project_type == 'python':
                result = subprocess.run(['pip', 'list', '--outdated', '--format=json'], 
                                     capture_output=True, text=True, cwd=self.repository_path)
                
                if result.returncode == 0:
                    try:
                        outdated_data = json.loads(result.stdout)
                        for pkg in outdated_data:
                            outdated.append({
                                "package": pkg.get('name'),
                                "current_version": pkg.get('version'),
                                "latest_version": pkg.get('latest_version'),
                                "type": pkg.get('latest_filetype')
                            })
                    except json.JSONDecodeError:
                        pass
            
            elif project_type == 'javascript':
                result = subprocess.run(['npm', 'outdated', '--json'], 
                                     capture_output=True, text=True, cwd=self.repository_path)
                
                if result.stdout:
                    try:
                        outdated_data = json.loads(result.stdout)
                        for pkg, info in outdated_data.items():
                            outdated.append({
                                "package": pkg,
                                "current_version": info.get('current'),
                                "wanted_version": info.get('wanted'),
                                "latest_version": info.get('latest')
                            })
                    except json.JSONDecodeError:
                        pass
                        
        except FileNotFoundError:
            pass
        
        return outdated
    
    def _check_license_compatibility(self, project_type: str) -> List[Dict[str, Any]]:
        """Check for license compatibility issues."""
        license_issues = []
        
        # This is a simplified license check
        # A full implementation would need a comprehensive license database
        
        restrictive_licenses = [
            'GPL-3.0', 'GPL-2.0', 'AGPL-3.0', 'LGPL-3.0', 'LGPL-2.1'
        ]
        
        permissive_licenses = [
            'MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC'
        ]
        
        license_issues.append({
            "note": "License checking requires manual review or specialized tools",
            "suggestions": [
                "Use tools like 'license-checker' for npm projects",
                "Use 'pip-licenses' for Python projects",
                "Review all dependency licenses manually",
                f"Avoid restrictive licenses: {', '.join(restrictive_licenses)}"
            ]
        })
        
        return license_issues
    
    def _generate_dependency_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable suggestions based on dependency analysis."""
        suggestions = []
        
        # Vulnerability suggestions
        if results["vulnerabilities"]:
            vuln_count = len([v for v in results["vulnerabilities"] if 'package' in v])
            if vuln_count > 0:
                suggestions.append(f"Found {vuln_count} security vulnerabilities - update affected packages")
                suggestions.append("Run dependency security scanning regularly")
        
        # Outdated package suggestions
        if results["outdated_packages"]:
            outdated_count = len(results["outdated_packages"])
            suggestions.append(f"Found {outdated_count} outdated packages - consider updating")
            suggestions.append("Set up automated dependency updates (e.g., Dependabot)")
        
        # Project-specific suggestions
        project_type = results.get("project_type")
        if project_type == 'python':
            suggestions.extend([
                "Consider pinning dependency versions in requirements.txt",
                "Use virtual environments to isolate dependencies",
                "Add requirements-dev.txt for development dependencies"
            ])
        elif project_type == 'javascript':
            suggestions.extend([
                "Use package-lock.json or yarn.lock for reproducible builds",
                "Regularly run 'npm audit' to check for vulnerabilities",
                "Consider using 'npm ci' in production environments"
            ])
        elif project_type == 'java':
            suggestions.extend([
                "Use dependency management plugins (Maven/Gradle)",
                "Configure OWASP Dependency Check for security scanning",
                "Keep build tools and plugins updated"
            ])
        
        return suggestions
    
    def update_dependencies(self, package_names: List[str] = None, 
                          update_type: str = 'minor', dry_run: bool = True) -> Dict[str, Any]:
        """Update project dependencies."""
        project_type = self._detect_project_type()
        
        results = {
            "project_type": project_type,
            "update_type": update_type,
            "dry_run": dry_run,
            "updated_packages": [],
            "failed_updates": [],
            "suggestions": []
        }
        
        try:
            if project_type == 'python':
                return self._update_python_dependencies(package_names, update_type, dry_run, results)
            elif project_type == 'javascript':
                return self._update_javascript_dependencies(package_names, update_type, dry_run, results)
            elif project_type == 'java':
                return self._update_java_dependencies(package_names, update_type, dry_run, results)
            else:
                results["error"] = f"Dependency updates not supported for {project_type}"
                return results
                
        except Exception as e:
            results["error"] = f"Dependency update failed: {str(e)}"
            return results
    
    def _update_python_dependencies(self, package_names: List[str], update_type: str, 
                                   dry_run: bool, results: Dict[str, Any]) -> Dict[str, Any]:
        """Update Python dependencies."""
        if not package_names:
            # Update all packages
            cmd = ['pip', 'list', '--outdated', '--format=json']
            if dry_run:
                results["suggestions"].append("Run 'pip install --upgrade <package>' to update packages")
                return results
        else:
            # Update specific packages
            for package in package_names:
                cmd = ['pip', 'install', '--upgrade', package]
                if dry_run:
                    results["suggestions"].append(f"Would update: {package}")
                else:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repository_path)
                        if result.returncode == 0:
                            results["updated_packages"].append(package)
                        else:
                            results["failed_updates"].append({
                                "package": package,
                                "error": result.stderr
                            })
                    except Exception as e:
                        results["failed_updates"].append({
                            "package": package,
                            "error": str(e)
                        })
        
        return results
    
    def _update_javascript_dependencies(self, package_names: List[str], update_type: str, 
                                      dry_run: bool, results: Dict[str, Any]) -> Dict[str, Any]:
        """Update JavaScript dependencies."""
        if not package_names:
            # Update all packages
            cmd = ['npm', 'update']
            if update_type == 'major':
                cmd = ['npm', 'update', '--save']
        else:
            # Update specific packages
            cmd = ['npm', 'install'] + [f"{pkg}@latest" for pkg in package_names]
        
        if dry_run:
            results["suggestions"].append(f"Would run: {' '.join(cmd)}")
        else:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repository_path)
                if result.returncode == 0:
                    results["updated_packages"] = package_names or ["all packages"]
                else:
                    results["failed_updates"].append({
                        "command": ' '.join(cmd),
                        "error": result.stderr
                    })
            except Exception as e:
                results["error"] = str(e)
        
        return results
    
    def _update_java_dependencies(self, package_names: List[str], update_type: str, 
                                 dry_run: bool, results: Dict[str, Any]) -> Dict[str, Any]:
        """Update Java dependencies."""
        results["suggestions"].extend([
            "Java dependency updates typically require manual pom.xml/build.gradle editing",
            "Use 'mvn versions:display-dependency-updates' to check for updates",
            "Use 'gradle dependencyUpdates' task to check for updates"
        ])
        
        return results
    
    def generate_dependency_report(self, output_format: str = 'json') -> Dict[str, Any]:
        """Generate a comprehensive dependency report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "repository_path": self.repository_path,
            "analysis": self.analyze_dependencies(),
            "recommendations": []
        }
        
        # Add recommendations based on analysis
        analysis = report["analysis"]
        
        if analysis.get("vulnerabilities"):
            report["recommendations"].append({
                "priority": "high",
                "category": "security",
                "action": "Update packages with security vulnerabilities",
                "affected_packages": [v.get("package") for v in analysis["vulnerabilities"] if v.get("package")]
            })
        
        if analysis.get("outdated_packages"):
            report["recommendations"].append({
                "priority": "medium",
                "category": "maintenance",
                "action": "Update outdated packages",
                "affected_packages": [p.get("package") for p in analysis["outdated_packages"]]
            })
        
        # Save report if requested
        if output_format == 'json':
            report_file = os.path.join(self.repository_path, 'dependency_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            report["report_file"] = report_file
        
        return report


def analyze_dependencies(project_type: str = None, repository_path: str = None) -> Dict[str, Any]:
    """Analyze project dependencies."""
    manager = DependencyManager(repository_path)
    return manager.analyze_dependencies(project_type)


def update_dependencies(package_names: List[str] = None, update_type: str = 'minor', 
                       dry_run: bool = True, repository_path: str = None) -> Dict[str, Any]:
    """Update project dependencies."""
    manager = DependencyManager(repository_path)
    return manager.update_dependencies(package_names, update_type, dry_run)


def generate_dependency_report(output_format: str = 'json', repository_path: str = None) -> Dict[str, Any]:
    """Generate dependency report."""
    manager = DependencyManager(repository_path)
    return manager.generate_dependency_report(output_format)


def dependency_handler(action: str, **kwargs) -> Dict[str, Any]:
    """Handle dependency management requests."""
    manager = DependencyManager(kwargs.get('repository_path'))
    
    if action == 'analyze':
        return manager.analyze_dependencies(kwargs.get('project_type'))
    elif action == 'update':
        return manager.update_dependencies(
            kwargs.get('package_names'),
            kwargs.get('update_type', 'minor'),
            kwargs.get('dry_run', True)
        )
    elif action == 'report':
        return manager.generate_dependency_report(kwargs.get('output_format', 'json'))
    else:
        return {"error": f"Unknown action: {action}"}