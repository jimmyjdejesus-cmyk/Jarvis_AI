"""
Unit tests for CodeIntelligenceEngine
"""
import unittest
from tools.code_intelligence.engine import CodeIntelligenceEngine

class TestCodeIntelligenceEngine(unittest.TestCase):
    def test_initialization(self):
        engine = CodeIntelligenceEngine()
        self.assertIsNotNone(engine)

if __name__ == "__main__":
    unittest.main()
