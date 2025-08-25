import unittest
from unittest.mock import AsyncMock, MagicMock
import asyncio

from jarvis.agents.specialists import TestingAgent

class TestExecutionGuidedGeneration(unittest.TestCase):

    def test_generate_test_cases_success_first_try(self):
        # Mock the MCP client
        mcp_client = MagicMock()
        mcp_client.generate_response = AsyncMock(return_value={
            "response": """
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
"""
        })

        # Instantiate the TestingAgent
        agent = TestingAgent(mcp_client)

        # The code to be tested
        code_to_test = """
def add(a, b):
    return a + b
"""

        # Run the test
        result = asyncio.run(agent.generate_test_cases(code_to_test))

        # Assertions
        self.assertNotIn("error", result)
        self.assertEqual(result["execution_guided"]["status"], "success")
        self.assertEqual(result["execution_guided"]["retries"], 0)

    def test_generate_test_cases_self_correction(self):
        # Mock the MCP client to return a faulty response first, then a correct one
        mcp_client = MagicMock()
        mcp_client.generate_response = AsyncMock(side_effect=[
            {
                "response": """
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 4) # Intentionally wrong

if __name__ == '__main__':
    unittest.main()
"""
            },
            {
                "response": """
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
"""
            }
        ])

        # Instantiate the TestingAgent
        agent = TestingAgent(mcp_client)

        # The code to be tested
        code_to_test = """
def add(a, b):
    return a + b
"""

        # Run the test
        result = asyncio.run(agent.generate_test_cases(code_to_test))

        # Assertions
        self.assertNotIn("error", result)
        self.assertEqual(result["execution_guided"]["status"], "success")
        self.assertEqual(result["execution_guided"]["retries"], 1)

    def test_generate_test_cases_failure(self):
        # Mock the MCP client to always return a faulty response
        mcp_client = MagicMock()
        mcp_client.generate_response = AsyncMock(return_value={
            "response": "invalid code"
        })

        # Instantiate the TestingAgent
        agent = TestingAgent(mcp_client)

        # The code to be tested
        code_to_test = """
def add(a, b):
    return a + b
"""

        # Run the test
        result = asyncio.run(agent.generate_test_cases(code_to_test, max_retries=2))

        # Assertions
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main()
