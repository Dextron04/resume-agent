#!/usr/bin/env python3
"""Quick test script to verify fixes"""

# Mock anthropic before importing
from unittest.mock import patch, MagicMock
import sys

# Mock the anthropic module
mock_anthropic = MagicMock()
sys.modules['anthropic'] = mock_anthropic

from app.services.resume_agent import ResumeAIAgent

def test_tech_extraction():
    print("Testing technology extraction...")
    agent = ResumeAIAgent('', 'test-key', load_sentence_model=False)
    
    test_cases = [
        {
            "summary": "Technologies: Python, Flask, SQLite",
            "expected": ["Python", "Flask", "SQLite"]
        },
        {
            "summary": "Database: MongoDB",
            "expected": ["MongoDB"]
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        result = agent.extract_technologies_from_summary(test_case["summary"])
        print(f"\nTest {i+1}: {test_case['summary']}")
        print(f"Result: {result}")
        
        for expected_tech in test_case["expected"]:
            if expected_tech in result:
                print(f"✅ Found {expected_tech}")
            else:
                print(f"❌ Missing {expected_tech}")

if __name__ == "__main__":
    test_tech_extraction()
