#!/usr/bin/env python3
"""
Jarvis AI Enhanced Features Demo
Demonstrates the new capabilities added to Jarvis AI system.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.core import JarvisAgent
from agent.tools import run_tool
import agent.tools as tools


def demo_approval_callback(preview):
    """Simple approval callback for demo purposes."""
    print(f"🔍 Action Preview: {preview}")
    return True


def demonstrate_features():
    """Demonstrate all the new features."""
    print("🚀 Jarvis AI Enhanced Features Demo")
    print("=" * 50)
    
    # Create agent
    agent = JarvisAgent(
        persona_prompt="You are an advanced AI coding assistant.",
        tool_registry=tools,
        approval_callback=demo_approval_callback,
        user="demo_user"
    )
    
    # Test cases
    test_commands = [
        ("Git Commands", [
            "git status",
            "git diff",
            "git branch"
        ]),
        ("IDE Integration", [
            "open in pycharm agent/core.py:10",
            "open in intellij README.md"
        ]),
        ("Note-taking", [
            "save to notion Today I implemented new AI features",
            "save to onenote Meeting notes about code review"
        ]),
        ("Code Analysis", [
            "review code quality",
            "search code for JarvisAgent",
            "find function parse_natural_language"
        ]),
        ("Repository Context", [
            "show project structure",
            "repo context"
        ]),
        ("GitHub Integration", [
            "list issues",
            "create issue for documentation update"
        ])
    ]
    
    for category, commands in test_commands:
        print(f"\n📂 {category}")
        print("-" * 30)
        
        for i, command in enumerate(commands, 1):
            print(f"\n{i}. Testing: '{command}'")
            
            try:
                # Parse the command
                plan = agent.parse_natural_language(command, [])
                
                if plan:
                    tool_name = plan[0]['tool']
                    print(f"   ✅ Parsed as: {tool_name}")
                    
                    # Show what arguments were extracted
                    args = plan[0]['args']
                    print(f"   📋 Arguments: {list(args.keys())}")
                    
                    # For some tools, actually execute them
                    if tool_name in ['git_command', 'repo_context', 'code_search']:
                        try:
                            result = run_tool(plan[0], user="demo_user")
                            if tool_name == 'git_command':
                                if result.get('success'):
                                    print(f"   📤 Git Output: {result.get('stdout', '')[:100]}...")
                                else:
                                    print(f"   ❌ Git Error: {result.get('stderr', 'Unknown error')}")
                            elif tool_name == 'repo_context':
                                if isinstance(result, dict) and 'summary' in result:
                                    print(f"   📊 Context: {result['summary'][:100]}...")
                                else:
                                    print(f"   ❌ Context Error: {result}")
                            elif tool_name == 'code_search':
                                if isinstance(result, list):
                                    print(f"   🔍 Found: {len(result)} code results")
                                    if result:
                                        first = result[0]
                                        print(f"   📄 Sample: {first.get('file_path', 'unknown')} line {first.get('line_number', 0)}")
                                else:
                                    print(f"   ❌ Search Error: {result}")
                        except Exception as e:
                            print(f"   ⚠️  Execution Note: {str(e)[:100]}")
                    else:
                        print(f"   💡 Ready to execute (demo mode)")
                
                else:
                    print("   ❌ Not recognized by parser")
                    
            except Exception as e:
                print(f"   💥 Error: {str(e)}")
    
    print(f"\n🎉 Demo Complete!")
    print("\n📚 Summary of New Features:")
    print("• Git command integration (status, commit, diff, etc.)")
    print("• JetBrains IDE support (PyCharm, IntelliJ, WebStorm, etc.)")
    print("• Note-taking integration (Notion & OneNote)")
    print("• Advanced code review with quality analysis")
    print("• Semantic and lexical code search")
    print("• GitHub API integration for repository management")
    print("• Comprehensive repository context for LLM/RAG")
    print("• Enhanced natural language command parsing")


def show_configuration_help():
    """Show configuration instructions."""
    print("\n⚙️  Configuration Instructions:")
    print("=" * 40)
    print("\nTo use all features, set these environment variables:")
    print("• GITHUB_TOKEN - For GitHub API integration")
    print("• NOTION_TOKEN - For Notion integration")
    print("• NOTION_DATABASE_ID - Target Notion database")
    print("• ONENOTE_TOKEN - For OneNote integration")
    print("\nIDE Integration:")
    print("• Ensure JetBrains IDEs are installed and in PATH")
    print("• Supported: PyCharm, IntelliJ IDEA, WebStorm, PHPStorm, etc.")
    print("\nExample commands:")
    print("• git status")
    print("• open in pycharm src/main.py:42")
    print("• save to notion Today's progress notes")
    print("• review code quality")
    print("• search code for authenticate function")
    print("• create issue for bug fix")


if __name__ == "__main__":
    try:
        demonstrate_features()
        show_configuration_help()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()