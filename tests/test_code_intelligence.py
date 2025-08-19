#!/usr/bin/env python3
"""
Test Code Intelligence Engine
Simple test to validate the code intelligence functionality.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))
sys.path.insert(0, os.path.dirname(__file__))

from agent import code_intelligence


def test_code_context_extraction():
    """Test code context extraction functionality."""
    print("🧪 Testing Code Context Extraction...")
    
    # Create a temporary Python file for testing
    test_code = '''import os
import sys
from typing import List, Dict

class DataProcessor:
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.results = []
    
    def load_config(self, path: str) -> Dict:
        """Load configuration from file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def process_data(self, data: List[Dict]) -> List[Dict]:
        """Process a list of data items."""
        processed = []
        for item in data:
            # Process each item here
            if item.get('status') == 'active':
                processed.append(item)
        return processed
    
    def save_results(self, output_path: str):
        """Save processing results to file."""
        with open(output_path, 'w') as f:
            json.dump(self.results, f)

# Test function
def main():
    processor = DataProcessor('config.json')
    data = [{'id': 1, 'status': 'active'}]
    # This line needs completion
    '''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        # Test context extraction
        engine = code_intelligence.CodeIntelligenceEngine()
        context = engine.extract_code_context(temp_file, 27)  # Line with comment "This line needs completion"
        
        print(f"   ✅ File: {os.path.basename(context.file_path)}")
        print(f"   ✅ Current function: {context.current_function}")
        print(f"   ✅ Current class: {context.current_class}")
        print(f"   ✅ Imports found: {len(context.imports or [])}")
        print(f"   ✅ Local variables: {len(context.local_variables or [])}")
        
        if context.imports:
            print(f"      Imports: {', '.join(context.imports[:3])}")
        
        if context.local_variables:
            print(f"      Variables: {', '.join(context.local_variables[:5])}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass


def test_code_completion():
    """Test code completion generation."""
    print("🧪 Testing Code Completion Generation...")
    
    # Create a simple test file
    test_code = '''def calculate_sum(numbers):
    total = 0
    for num in numbers:
        # Complete this line
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        # Test convenience function
        completions = code_intelligence.get_code_completion(
            temp_file, 
            4,  # Line with "Complete this line" 
            0,
            model="llama3.2"
        )
        
        if completions and not any('error' in comp for comp in completions):
            print(f"   ✅ Generated {len(completions)} completion(s)")
            for i, comp in enumerate(completions, 1):
                print(f"      {i}. {comp.get('suggestion', 'No suggestion')[:50]}...")
        elif completions and 'error' in completions[0]:
            print(f"   ⚠️  Error (expected - Ollama may not be running): {completions[0]['error']}")
        else:
            print("   ⚠️  No completions generated")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass


def test_feedback_recording():
    """Test feedback recording functionality."""
    print("🧪 Testing Feedback Recording...")
    
    test_code = '''def hello_world():
    print("Hello, World!")
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        # Test feedback recording
        success = code_intelligence.record_completion_feedback(
            temp_file,
            2,  # Line 2
            0,
            'print("Hello, World!")',
            True,  # Accepted
            'test_user'
        )
        
        if success:
            print("   ✅ Feedback recorded successfully")
        else:
            print("   ❌ Failed to record feedback")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass


def test_database_tables():
    """Test database table creation."""
    print("🧪 Testing Database Tables...")
    
    try:
        # Initialize engine (creates tables)
        engine = code_intelligence.CodeIntelligenceEngine()
        
        import sqlite3
        conn = sqlite3.connect(engine.db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        tables = [
            'code_completion_feedback',
            'code_completion_analytics', 
            'successful_code_patterns'
        ]
        
        for table in tables:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            )
            result = cursor.fetchone()
            if result:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Code Intelligence Engine Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_tables,
        test_code_context_extraction,
        test_feedback_recording,
        test_code_completion,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - check Ollama connection and dependencies")
    
    return passed == total


if __name__ == "__main__":
    main()