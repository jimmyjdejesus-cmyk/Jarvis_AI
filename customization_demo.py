#!/usr/bin/env python3
"""
Jarvis AI Customization Demo
Demonstrates how to create and use custom workflows and integrations.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

def demo_custom_workflow():
    """Demonstrate custom workflow creation."""
    print("🎯 Custom Workflow Demo")
    print("=" * 30)
    
    # Example 1: Simple Custom Workflow
    class MyCustomWorkflow:
        def __init__(self, name):
            self.name = name
        
        def execute(self, query):
            print(f"🚀 Executing {self.name}")
            print(f"📝 Query: {query}")
            
            # Step 1: Planning
            plan = [
                "Analyze the query",
                "Research relevant information",
                "Generate comprehensive response"
            ]
            
            print("📋 Planning:")
            for i, step in enumerate(plan, 1):
                print(f"   {i}. {step}")
            
            # Step 2: Execution
            print("\n🔄 Execution:")
            results = {}
            for step in plan:
                print(f"   ✅ {step}")
                results[step] = f"Completed: {step}"
            
            # Step 3: Final Result
            final_result = f"""
Custom Workflow: {self.name}

Query: {query}

Results:
• Analysis completed successfully
• Research gathered relevant information  
• Response generated with comprehensive insights

Workflow executed {len(plan)} steps successfully.
"""
            
            print("\n📝 Final Result:")
            print(final_result)
            return final_result
    
    # Test the custom workflow
    workflow = MyCustomWorkflow("Demo Workflow")
    result = workflow.execute("How do I customize Jarvis AI workflows?")
    return result

def demo_custom_tools():
    """Demonstrate custom tool creation."""
    print("\n🛠️ Custom Tools Demo")
    print("=" * 25)
    
    # Example: Custom Calculator Tool
    class CalculatorTool:
        def __init__(self):
            self.name = "calculator"
            self.description = "Performs mathematical calculations"
        
        def execute(self, operation, numbers):
            print(f"🧮 Calculator: {operation} on {numbers}")
            
            if operation == "sum":
                result = sum(numbers)
            elif operation == "average":
                result = sum(numbers) / len(numbers)
            elif operation == "max":
                result = max(numbers)
            elif operation == "min":
                result = min(numbers)
            else:
                result = "Unknown operation"
            
            print(f"   Result: {result}")
            return result
    
    # Example: Text Analyzer Tool
    class TextAnalyzerTool:
        def __init__(self):
            self.name = "text_analyzer"
            self.description = "Analyzes text content"
        
        def execute(self, text):
            print(f"📝 Text Analyzer: Analyzing text...")
            
            analysis = {
                "character_count": len(text),
                "word_count": len(text.split()),
                "sentence_count": text.count('.') + text.count('!') + text.count('?'),
                "paragraph_count": text.count('\n\n') + 1
            }
            
            print(f"   Characters: {analysis['character_count']}")
            print(f"   Words: {analysis['word_count']}")
            print(f"   Sentences: {analysis['sentence_count']}")
            
            return analysis
    
    # Test the tools
    calc = CalculatorTool()
    calc.execute("sum", [1, 2, 3, 4, 5])
    calc.execute("average", [10, 20, 30])
    
    analyzer = TextAnalyzerTool()
    sample_text = "This is a sample text. It has multiple sentences! And some analysis features?"
    analyzer.execute(sample_text)

def demo_integration_pattern():
    """Demonstrate integration patterns."""
    print("\n🔌 Integration Pattern Demo")
    print("=" * 30)
    
    # Example: API Integration Pattern
    class APIIntegrationExample:
        def __init__(self):
            self.apis = {}
        
        def add_api(self, name, base_url, headers=None):
            self.apis[name] = {
                'base_url': base_url,
                'headers': headers or {}
            }
            print(f"✅ Added API: {name}")
        
        def make_request(self, api_name, endpoint, params=None):
            if api_name not in self.apis:
                print(f"❌ API {api_name} not found")
                return None
            
            api_config = self.apis[api_name]
            url = f"{api_config['base_url']}/{endpoint}"
            
            # Simulate API call
            print(f"🌐 Making request to {api_name}: {endpoint}")
            print(f"   URL: {url}")
            if params:
                print(f"   Params: {params}")
            
            # Return simulated response
            return {
                "status": "success",
                "data": f"Simulated response from {api_name}",
                "endpoint": endpoint
            }
    
    # Test the integration
    api_manager = APIIntegrationExample()
    api_manager.add_api("weather", "https://api.weather.com", {"API-Key": "demo"})
    api_manager.add_api("news", "https://newsapi.org", {"Authorization": "Bearer demo"})
    
    weather_data = api_manager.make_request("weather", "current", {"city": "New York"})
    news_data = api_manager.make_request("news", "headlines", {"category": "technology"})
    
    print(f"   Weather result: {weather_data['status']}")
    print(f"   News result: {news_data['status']}")

def demo_database_integration():
    """Demonstrate database integration."""
    print("\n🗄️ Database Integration Demo")
    print("=" * 30)
    
    # Simple in-memory database simulation
    class SimpleDatabase:
        def __init__(self):
            self.data = {}
            self.workflows = []
        
        def store_data(self, key, value):
            self.data[key] = value
            print(f"💾 Stored: {key} = {value}")
        
        def get_data(self, key):
            value = self.data.get(key, "Not found")
            print(f"📖 Retrieved: {key} = {value}")
            return value
        
        def save_workflow_result(self, workflow_name, result):
            workflow_entry = {
                "name": workflow_name,
                "result": result,
                "timestamp": "2025-08-20 12:00:00"
            }
            self.workflows.append(workflow_entry)
            print(f"📊 Saved workflow: {workflow_name}")
        
        def get_workflow_history(self, limit=5):
            history = self.workflows[-limit:]
            print(f"📈 Retrieved {len(history)} workflow entries")
            for entry in history:
                print(f"   {entry['name']}: {entry['timestamp']}")
            return history
    
    # Test the database
    db = SimpleDatabase()
    db.store_data("user_preference", "dark_theme")
    db.store_data("last_query", "How to customize workflows?")
    
    theme = db.get_data("user_preference")
    query = db.get_data("last_query")
    
    db.save_workflow_result("Custom Demo", "Successfully completed")
    db.save_workflow_result("Integration Test", "All tests passed")
    
    history = db.get_workflow_history()

def show_customization_examples():
    """Show practical customization examples."""
    print("\n💡 Practical Customization Examples")
    print("=" * 40)
    
    examples = [
        {
            "name": "Document Processor",
            "description": "Process PDFs, DOCX, and text files",
            "use_case": "Extract text, analyze content, generate summaries",
            "file": "custom_workflows/document_processor.py"
        },
        {
            "name": "Social Media Monitor", 
            "description": "Monitor social platforms for mentions",
            "use_case": "Brand monitoring, sentiment analysis, trend detection",
            "file": "custom_workflows/social_monitor.py"
        },
        {
            "name": "Email Automation",
            "description": "Process emails and generate responses",
            "use_case": "Customer support, email classification, auto-replies",
            "file": "custom_workflows/email_processor.py"
        },
        {
            "name": "Data Pipeline",
            "description": "Real-time data processing and analysis",
            "use_case": "ETL processes, data transformation, analytics",
            "file": "integrations/data_pipeline.py"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. 📁 {example['name']}")
        print(f"   Description: {example['description']}")
        print(f"   Use Case: {example['use_case']}")
        print(f"   Implementation: {example['file']}")

def main():
    """Main demonstration function."""
    print("🤖 JARVIS AI - CUSTOMIZATION DEMONSTRATION")
    print("=" * 50)
    
    print("This demo shows how to customize and extend Jarvis AI")
    print("with your own workflows, tools, and integrations.\n")
    
    # Run all demonstrations
    demo_custom_workflow()
    demo_custom_tools()
    demo_integration_pattern()
    demo_database_integration()
    show_customization_examples()
    
    print("\n" + "=" * 50)
    print("✅ Customization Demo Complete!")
    print("\n📚 Next Steps:")
    print("1. Review CUSTOMIZATION_GUIDE.md for detailed instructions")
    print("2. Explore the template files in custom_workflows/")
    print("3. Check integration examples in integrations/")
    print("4. Start building your own custom workflows!")
    print("\n🚀 Happy customizing!")

if __name__ == "__main__":
    main()
