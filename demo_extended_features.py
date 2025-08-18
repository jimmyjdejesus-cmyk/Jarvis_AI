#!/usr/bin/env python3
"""
Extended Code Agent Usability Demo
Demonstrates the new features added to Jarvis AI for enhanced developer productivity.
"""
import os
import sys
import json
from typing import Dict, Any

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

import test_generator
import doc_generator
import dependency_manager
import persona_manager
import github_integration


def demo_header(title: str) -> None:
    """Print a formatted demo section header."""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)


def demo_test_generation() -> None:
    """Demo test generation capabilities."""
    demo_header("Test Generation and Coverage Analysis")
    
    # Create a sample Python file for testing
    sample_file = "/tmp/sample_calculator.py"
    sample_code = '''def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract second number from first."""
    return a - b

class Calculator:
    """A simple calculator class."""
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a, b):
        """Divide first number by second."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
'''
    
    with open(sample_file, 'w') as f:
        f.write(sample_code)
    
    print(f"📝 Generated sample file: {sample_file}")
    
    # Generate tests
    print("\n🧪 Generating tests...")
    result = test_generator.generate_tests_for_file(sample_file, test_type='unit', framework='pytest')
    
    if 'error' not in result:
        print(f"✅ Tests generated: {result['test_file_path']}")
        print(f"📊 Functions found: {len(result['generated_tests'])}")
        print(f"🔧 Framework: {result['framework']}")
        
        # Show generated test file content
        if result['test_file_path'] and os.path.exists(result['test_file_path']):
            print(f"\n📄 Generated test file preview:")
            with open(result['test_file_path'], 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:2d}: {line.rstrip()}")
                if len(lines) > 20:
                    print("    ... (truncated)")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Analyze test coverage
    print("\n📈 Analyzing test coverage...")
    coverage_result = test_generator.analyze_test_coverage(sample_file)
    
    if 'error' not in coverage_result:
        print(f"✅ Coverage analysis completed")
        if coverage_result.get('suggestions'):
            print("💡 Suggestions:")
            for suggestion in coverage_result['suggestions'][:3]:
                print(f"   • {suggestion}")
    else:
        print(f"❌ Coverage analysis error: {coverage_result.get('error', 'Unknown error')}")


def demo_documentation_generation() -> None:
    """Demo documentation generation capabilities."""
    demo_header("Automated Documentation Generation")
    
    # Use the same sample file
    sample_file = "/tmp/sample_calculator.py"
    
    print(f"📝 Generating documentation for: {sample_file}")
    
    # Generate documentation
    result = doc_generator.generate_documentation(
        sample_file, 
        doc_format='markdown', 
        include_private=False,
        output_dir='/tmp/docs'
    )
    
    if 'error' not in result:
        print(f"✅ Documentation generated in: {result['output_dir']}")
        print(f"📊 Files processed: {result['summary']['total_files']}")
        print(f"🔧 Functions documented: {result['summary']['documented_functions']}")
        print(f"📝 Classes documented: {result['summary']['documented_classes']}")
        
        # Show generated files
        print(f"\n📄 Generated files:")
        for file_path in result['generated_files']:
            print(f"   • {os.path.basename(file_path)}")
        
        # Show a preview of the generated documentation
        if result['generated_files']:
            doc_file = result['generated_files'][0]
            if os.path.exists(doc_file):
                print(f"\n📖 Documentation preview ({os.path.basename(doc_file)}):")
                with open(doc_file, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:15], 1):
                        print(f"{i:2d}: {line.rstrip()}")
                    if len(lines) > 15:
                        print("    ... (truncated)")
        
        if result['summary']['missing_docstrings']:
            print(f"\n⚠️  Missing docstrings:")
            for missing in result['summary']['missing_docstrings'][:3]:
                print(f"   • {missing}")
    else:
        print(f"❌ Error: {result['error']}")


def demo_dependency_management() -> None:
    """Demo dependency management capabilities."""
    demo_header("Dependency Management and Security Analysis")
    
    # Create a sample requirements.txt for testing
    sample_requirements = "/tmp/requirements.txt"
    requirements_content = '''flask==2.0.1
requests>=2.25.0
numpy==1.21.0
pandas>=1.3.0
pytest==6.2.4
black==21.5b0
'''
    
    with open(sample_requirements, 'w') as f:
        f.write(requirements_content)
    
    print(f"📝 Created sample requirements.txt: {sample_requirements}")
    
    # Analyze dependencies
    print("\n🔍 Analyzing dependencies...")
    result = dependency_manager.analyze_dependencies('python')
    
    if 'error' not in result:
        print(f"✅ Analysis completed for {result['project_type']} project")
        print(f"📊 Dependency files found: {len(result['dependency_files'])}")
        
        # Show dependency statistics
        total_deps = 0
        for file_path, deps in result['dependencies'].items():
            if isinstance(deps, dict) and 'total_count' in deps:
                total_deps += deps['total_count']
                print(f"   • {os.path.basename(file_path)}: {deps['total_count']} packages")
        
        print(f"📦 Total dependencies: {total_deps}")
        
        # Show vulnerabilities if any
        if result['vulnerabilities']:
            print(f"🚨 Security alerts: {len(result['vulnerabilities'])}")
            for vuln in result['vulnerabilities'][:3]:
                if 'package' in vuln:
                    print(f"   • {vuln['package']}: {vuln.get('advisory', 'Security issue')}")
        
        # Show outdated packages
        if result['outdated_packages']:
            print(f"📅 Outdated packages: {len(result['outdated_packages'])}")
            for pkg in result['outdated_packages'][:3]:
                print(f"   • {pkg['package']}: {pkg['current_version']} → {pkg['latest_version']}")
        
        # Show suggestions
        if result['suggestions']:
            print(f"\n💡 Recommendations:")
            for suggestion in result['suggestions'][:4]:
                print(f"   • {suggestion}")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Generate dependency report
    print("\n📋 Generating dependency report...")
    report = dependency_manager.generate_dependency_report('json')
    
    if 'error' not in report:
        print(f"✅ Report generated: {report.get('report_file', 'In memory')}")
        print(f"🕒 Generated at: {report['generated_at']}")
        
        if report['recommendations']:
            print(f"🎯 Priority recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec['priority'].upper()}: {rec['action']}")


def demo_persona_management() -> None:
    """Demo persona management capabilities."""
    demo_header("Customizable Agent Personas")
    
    # List available personas
    print("👥 Available personas:")
    personas = persona_manager.list_available_personas()
    
    for persona in personas[:6]:  # Show first 6
        print(f"   • {persona['name']}: {persona['description']}")
        print(f"     Focus: {', '.join(persona['focus_areas'][:3])}")
        print(f"     Style: {persona['communication_style']}")
        print()
    
    # Demo persona recommendation
    print("🎯 Persona recommendations for different tasks:")
    
    tasks = [
        ("code_review", "Code Review"),
        ("security_review", "Security Analysis"),
        ("performance_optimization", "Performance Optimization"),
        ("learning", "Learning/Mentoring")
    ]
    
    for task_type, task_name in tasks:
        recommendations = persona_manager.recommend_persona_for_task(task_type)
        print(f"   • {task_name}: {', '.join(recommendations[:2])}")
    
    # Demo custom persona creation
    print(f"\n🛠️  Creating custom persona...")
    try:
        manager = persona_manager.get_persona_manager()
        custom_persona = manager.create_custom_persona(
            name="API Designer",
            description="Specialist in REST API design and best practices",
            personality_traits=["systematic", "standards-focused", "user-centric"],
            focus_areas=["api_design", "rest_principles", "documentation", "versioning"],
            communication_style="structured_and_methodical",
            review_criteria={
                "api_design": 10,
                "documentation": 9,
                "consistency": 9,
                "usability": 8,
                "performance": 7
            }
        )
        print(f"✅ Custom persona created: {custom_persona.name}")
        print(f"   Focus areas: {', '.join(custom_persona.focus_areas)}")
        
    except Exception as e:
        print(f"❌ Error creating custom persona: {e}")
    
    # Demo prompt generation
    print(f"\n💬 Sample persona prompts:")
    sample_input = "How should I structure my REST API endpoints?"
    
    for persona_name in ["Senior Developer", "Security Expert"]:
        prompt = persona_manager.get_persona_prompt(persona_name, sample_input)
        print(f"\n🎭 {persona_name} prompt preview:")
        print(f"   {prompt[:200]}...")


def demo_github_cicd_integration() -> None:
    """Demo GitHub CI/CD integration capabilities."""
    demo_header("GitHub Actions CI/CD Integration")
    
    print("🔧 Available CI/CD workflow templates:")
    
    # Get workflow templates
    github_client = github_integration.GitHubIntegration()
    
    print("   • python_ci: Python CI with testing and coverage")
    print("   • node_ci: Node.js CI with multiple versions") 
    print("   • docker_build: Docker build and push to registry")
    print("   • deployment: Deployment automation")
    
    print(f"\n📋 CI/CD setup simulation:")
    print(f"   🐍 For Python projects:")
    print(f"      • Set up pytest with coverage reporting")
    print(f"      • Add code quality checks (flake8, black)")
    print(f"      • Configure multi-version testing")
    print(f"      • Set up deployment pipeline")
    
    print(f"\n   🌐 For Node.js projects:")
    print(f"      • Set up Jest testing framework")
    print(f"      • Add ESLint and Prettier checks")
    print(f"      • Configure npm audit for security")
    print(f"      • Set up deployment to hosting service")
    
    print(f"\n   🐳 For Docker projects:")
    print(f"      • Set up multi-stage builds")
    print(f"      • Configure security scanning")
    print(f"      • Set up container registry push")
    print(f"      • Add deployment automation")
    
    # Demo security features
    print(f"\n🔒 Security features:")
    print(f"   • Dependabot alerts for vulnerable dependencies")
    print(f"   • Code scanning with CodeQL")
    print(f"   • Security policy enforcement")
    print(f"   • Automated security fix pull requests")
    
    # Demo issue triage
    print(f"\n🏷️  Automated issue triage:")
    print(f"   • Auto-labeling based on content analysis")
    print(f"   • Priority assignment using keywords")
    print(f"   • Team member assignment based on expertise")
    print(f"   • Automated milestone assignment")


def demo_enhanced_code_review() -> None:
    """Demo enhanced code review capabilities."""
    demo_header("Enhanced Code Review with Refactoring Suggestions")
    
    # Create a sample code file with issues
    sample_file = "/tmp/sample_code_review.py"
    sample_code = '''import os, sys, json
import requests

def process_user_data(data):
    results = []
    for item in data:
        if item["status"] == "active":
            user_id = item["id"]
            name = item["name"]
            email = item["email"]
            if "@" in email and "." in email:
                user_info = {"id": user_id, "name": name, "email": email}
                response = requests.get(f"https://api.example.com/users/{user_id}")
                if response.status_code == 200:
                    additional_data = response.json()
                    user_info.update(additional_data)
                    results.append(user_info)
    return results

class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, user):
        self.users.append(user)
    
    def get_user(self, user_id):
        for user in self.users:
            if user["id"] == user_id:
                return user
        return None
'''
    
    with open(sample_file, 'w') as f:
        f.write(sample_code)
    
    print(f"📝 Created sample code file: {sample_file}")
    
    # Perform code review
    print(f"\n🔍 Performing comprehensive code review...")
    
    import code_review
    result = code_review.review_file(
        sample_file, 
        check_types=['style', 'security', 'complexity', 'best_practices']
    )
    
    if 'error' not in result:
        print(f"✅ Code review completed")
        print(f"📊 Overall score: {result.get('overall_score', 0)}/100")
        
        # Show issues found
        if result.get('issues'):
            print(f"\n⚠️  Issues found ({len(result['issues'])}):")
            for issue in result['issues'][:5]:
                print(f"   • Line {issue.get('line', '?')}: {issue.get('message', 'Issue found')}")
                print(f"     Type: {issue.get('type', 'unknown')} | Severity: {issue.get('severity', 'medium')}")
        
        # Show suggestions
        if result.get('suggestions'):
            print(f"\n💡 Refactoring suggestions:")
            for suggestion in result['suggestions'][:4]:
                print(f"   • {suggestion}")
        
        # Show metrics
        if result.get('metrics'):
            print(f"\n📈 Code metrics:")
            for metric, value in result['metrics'].items():
                print(f"   • {metric}: {value}")
    else:
        print(f"❌ Error: {result['error']}")


def main() -> None:
    """Run the extended code agent usability demo."""
    print("🎉 Jarvis AI - Extended Code Agent Usability Demo")
    print("=" * 60)
    print("Demonstrating enhanced features for developer productivity")
    
    # Create temp directory for demo files
    os.makedirs('/tmp/docs', exist_ok=True)
    os.makedirs('/tmp/tests', exist_ok=True)
    
    try:
        # Run all demos
        demo_test_generation()
        demo_documentation_generation()
        demo_dependency_management()
        demo_persona_management()
        demo_github_cicd_integration()
        demo_enhanced_code_review()
        
        print(f"\n" + "="*60)
        print("🎯 Demo Summary")
        print("="*60)
        print("✅ Test Generation: Automated unit test creation and coverage analysis")
        print("✅ Documentation: Auto-generated docs from code structure and comments")
        print("✅ Dependencies: Security scanning and update management")
        print("✅ Personas: Customizable agent behaviors for different coding styles")
        print("✅ CI/CD: GitHub Actions integration with workflow templates")
        print("✅ Code Review: Enhanced analysis with refactoring suggestions")
        
        print(f"\n💡 Key Benefits:")
        print("   • Faster development cycles with automated testing")
        print("   • Improved code quality through enhanced review processes")
        print("   • Better security with dependency vulnerability scanning")
        print("   • Streamlined CI/CD setup with pre-configured templates")
        print("   • Personalized developer experience with custom agent personas")
        print("   • Comprehensive documentation generation")
        
        print(f"\n🚀 Ready to enhance your development workflow!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup demo files
        import glob
        for pattern in ['/tmp/sample_*.py', '/tmp/requirements.txt']:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                except:
                    pass


if __name__ == "__main__":
    main()