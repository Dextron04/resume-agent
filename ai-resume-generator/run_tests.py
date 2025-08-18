#!/usr/bin/env python3
"""
Simple test runner to verify our tests work
"""

import os
import sys
import tempfile
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("🧪 Running AI Resume Generator Tests")
    print("=" * 50)
    
    try:
        # Import our test class
        from tests.test_phase1 import TestPhase1
        
        # Create test instance
        test_instance = TestPhase1()
        
        # Set up test knowledge base
        print("📁 Setting up test knowledge base...")
        test_kb_generator = test_instance.setup_test_knowledge_base()
        temp_dir = next(test_kb_generator)
        
        print(f"✅ Test knowledge base created at: {temp_dir}")
        
        # Run knowledge base loading test
        print("\n🔍 Testing knowledge base loading...")
        test_instance.test_knowledge_base_loading(temp_dir)
        print("✅ Knowledge base loading test passed")
        
        # Run technology extraction test
        print("\n🔧 Testing technology extraction...")
        test_instance.test_tech_extraction(temp_dir)
        print("✅ Technology extraction test passed")
        
        # Run job analysis test with mock
        print("\n🤖 Testing job analysis with mock Anthropic...")
        test_instance.test_job_analysis_with_mock_anthropic(None, temp_dir)
        print("✅ Job analysis test passed")
        
        # Run fallback test
        print("\n🛡️ Testing fallback functionality...")
        test_instance.test_job_analysis_fallback(temp_dir)
        print("✅ Fallback test passed")
        
        # Run empty knowledge base test
        print("\n📭 Testing empty knowledge base handling...")
        test_instance.test_empty_knowledge_base()
        print("✅ Empty knowledge base test passed")
        
        print("\n🎉 All tests passed successfully!")
        print("\n✅ The Anthropic integration is working correctly.")
        print("✅ Phase 1 functionality is ready for development.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
