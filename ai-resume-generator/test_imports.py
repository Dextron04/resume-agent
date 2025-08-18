#!/usr/bin/env python3
"""
Simple test to check if we can import the basic modules
"""

try:
    print("Testing basic imports...")
    
    # Test Anthropic
    print("Importing anthropic...")
    import anthropic
    print("✅ Anthropic imported")
    
    # Test other core modules
    print("Importing numpy...")
    import numpy
    print("✅ Numpy imported")
    
    print("Importing scikit-learn...")
    import sklearn
    print("✅ Scikit-learn imported")
    
    # Test our app modules
    print("Importing app.models...")
    from app.models import ProjectModel, ExperienceModel, JobAnalysisModel
    print("✅ App models imported")
    
    print("\n🎉 All basic imports successful!")
    print("Now testing ResumeAIAgent with sentence_model disabled...")
    
    # Test the agent without sentence model
    from app.services.resume_agent import ResumeAIAgent
    print("✅ ResumeAIAgent imported successfully")
    
    print("\n✅ All tests passed! The system is ready for testing.")

except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
