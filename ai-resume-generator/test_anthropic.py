#!/usr/bin/env python3
"""
Test script to verify Anthropic Claude integration
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.resume_agent import ResumeAIAgent

def create_test_knowledge_base(temp_dir):
    """Create a minimal test knowledge base"""
    import json
    
    # Create github_projects directory
    projects_dir = os.path.join(temp_dir, "github_projects")
    os.makedirs(projects_dir)
    
    # Create a sample project
    test_project = {
        "metadata": {
            "project_number": 1,
            "total_projects": 1,
            "user_name": "Test User"
        },
        "project": {
            "title": "ConnectX",
            "summary": "**Technologies Used:**\nReact, Node.js, Socket.io, PostgreSQL",
            "raw_summary": "Real-time chat application"
        }
    }
    
    with open(os.path.join(projects_dir, "01_connectx.json"), 'w') as f:
        json.dump(test_project, f)
    
    # Create minimal work experience
    work_exp_dir = os.path.join(temp_dir, "work_experience")
    os.makedirs(work_exp_dir)
    
    test_experience = {
        "work_experience": {
            "positions": [{
                "company": "Test Company",
                "position": "Software Engineer",
                "duration": "2024-2025"
            }]
        }
    }
    
    with open(os.path.join(work_exp_dir, "work_experience.json"), 'w') as f:
        json.dump(test_experience, f)
    
    # Create minimal skills
    skills_dir = os.path.join(temp_dir, "skills")
    os.makedirs(skills_dir)
    
    test_skills = {
        "skills": {
            "categories": {
                "programming_languages": {
                    "skills": [{"name": "Python", "proficiency": "Advanced"}]
                }
            }
        }
    }
    
    with open(os.path.join(skills_dir, "skills.json"), 'w') as f:
        json.dump(test_skills, f)
    
    # Create profile summary
    profile_summary = {
        "profile_summary": {
            "personal_info": {
                "name": "Test User",
                "title": "Software Engineer"
            }
        }
    }
    
    with open(os.path.join(temp_dir, "profile_summary.json"), 'w') as f:
        json.dump(profile_summary, f)

def test_anthropic_integration():
    """Test the Anthropic Claude integration"""
    
    # Load environment variables
    load_dotenv()
    
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your Anthropic API key in the .env file")
        return False
    
    print("✅ Anthropic API key found")
    
    # Create temporary knowledge base
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Creating test knowledge base in {temp_dir}")
        create_test_knowledge_base(temp_dir)
        
        try:
            # Initialize the agent
            print("🤖 Initializing ResumeAIAgent with Anthropic...")
            agent = ResumeAIAgent(temp_dir, anthropic_api_key)
            print("✅ Agent initialized successfully")
            
            # Test knowledge base loading
            print(f"📊 Loaded {len(agent.knowledge_base.projects)} projects")
            print(f"💼 Loaded {len(agent.knowledge_base.experience)} work experiences")
            
            # Test job analysis with Claude
            print("🔍 Testing job description analysis with Claude...")
            job_desc = """
            We are looking for a React developer with Node.js experience to join our frontend team.
            The ideal candidate should have experience with modern JavaScript, RESTful APIs, and real-time applications.
            Experience with PostgreSQL and Socket.io is a plus.
            """
            
            analysis = agent.analyze_job_description(job_desc)
            print("✅ Job analysis completed successfully")
            print(f"📋 Required skills: {analysis.required_skills}")
            print(f"🔑 Keywords: {analysis.keywords}")
            print(f"💼 Job title: {analysis.job_title}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🧪 Testing Anthropic Claude Integration for AI Resume Generator")
    print("=" * 60)
    
    success = test_anthropic_integration()
    
    if success:
        print("\n🎉 All tests passed! Anthropic integration is working correctly.")
        print("\n🚀 You can now run the full system with:")
        print("   cd /path/to/ai-resume-generator")
        print("   python -m pytest tests/test_phase1.py -v")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n💥 Tests failed! Please check the error messages above.")
        sys.exit(1)
