#!/usr/bin/env python3
"""
Test Phase 2 functionality - Semantic Matching & Intelligent Project Selection
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_knowledge_base_summary():
    """Test knowledge base summary"""
    print("\n📊 Testing knowledge base summary...")
    response = requests.get(f"{BASE_URL}/api/knowledge-base/summary")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Projects: {data['summary']['total_projects']}")
    print(f"Experiences: {data['summary']['total_experience']}")
    return response.status_code == 200

def test_project_relevance():
    """Test Phase 2: Project relevance calculation"""
    print("\n🎯 Testing Phase 2: Project relevance calculation...")
    
    job_description = """
    We are looking for a Full Stack Developer with strong experience in React and Node.js.
    The ideal candidate will have experience building modern web applications, working with
    databases like PostgreSQL, and deploying applications using Docker and AWS.
    
    Key Requirements:
    - 3+ years of React development
    - Experience with Node.js and Express
    - Database design and optimization
    - RESTful API development
    - Cloud deployment experience
    
    Nice to have:
    - TypeScript experience
    - DevOps knowledge
    - Microservices architecture
    """
    
    payload = {
        "job_description": job_description,
        "max_projects": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/calculate-project-relevance",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📈 Analysis Results:")
        print(f"Required Skills: {data['job_analysis']['required_skills']}")
        print(f"Technologies: {data['job_analysis']['technologies']}")
        print(f"Total Projects Analyzed: {data['total_projects_analyzed']}")
        
        print(f"\n🏆 Top Relevant Projects:")
        for i, project in enumerate(data['relevant_projects'][:3], 1):
            print(f"{i}. {project['project']['title']} (Score: {project['relevance_score']})")
            print(f"   Technologies: {', '.join(project['project']['technologies'])}")
            print(f"   Match Reasons: {', '.join(project['match_reasons'])}")
            print()
        
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_tailored_content_generation():
    """Test Phase 2: Complete tailored content generation"""
    print("\n🎨 Testing Phase 2: Tailored content generation...")
    
    job_description = """
    Senior React Developer position at a growing fintech startup. We need someone
    experienced in building scalable frontend applications with React, TypeScript,
    and modern tooling. Backend knowledge with Node.js is a plus.
    
    Requirements:
    - 4+ years React experience
    - TypeScript proficiency
    - State management (Redux/Context)
    - API integration experience
    - Modern build tools (Webpack, Vite)
    
    Bonus:
    - Node.js/Express experience
    - Financial services background
    - AWS/Docker knowledge
    """
    
    payload = {
        "job_description": job_description,
        "max_projects": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/api/generate-tailored-content",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        tailored = data['tailored_content']
        
        print(f"🎯 Job Analysis:")
        job_analysis = tailored['job_analysis']
        print(f"Required Skills: {job_analysis['required_skills']}")
        print(f"Job Title: {job_analysis.get('job_title', 'N/A')}")
        print(f"Experience Level: {job_analysis.get('experience_level', 'N/A')}")
        
        print(f"\n📂 Selected Projects ({len(tailored['selected_projects'])}):")
        for project in tailored['selected_projects']:
            print(f"• {project['project']['title']} (Score: {project['relevance_score']:.3f})")
            print(f"  Technologies: {', '.join(project['project']['technologies'])}")
            if project['match_reasons']:
                print(f"  Why selected: {', '.join(project['match_reasons'])}")
            print()
        
        print(f"💼 Selected Experiences ({len(tailored['selected_experiences'])}):")
        for exp in tailored['selected_experiences']:
            print(f"• {exp['experience']['position']} at {exp['experience']['company']} (Score: {exp['relevance_score']:.3f})")
            print(f"  Technologies: {', '.join(exp['experience']['technologies'])}")
            print()
        
        print(f"📝 Optimized Summary:")
        print(f"{tailored['optimized_summary']}")
        
        print(f"\n📊 Optimization Metadata:")
        meta = tailored['optimization_metadata']
        print(f"Projects available: {meta['total_projects_available']}")
        print(f"Projects selected: {meta['projects_selected']}")
        print(f"Experiences selected: {meta['experiences_selected']}")
        
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("🚀 AI Resume Generator - Phase 2 Testing")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Knowledge Base Summary", test_knowledge_base_summary),
        ("Project Relevance Calculation", test_project_relevance),
        ("Tailored Content Generation", test_tailored_content_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASS" if success else "❌ FAIL"))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, "❌ ERROR"))
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    for test_name, result in results:
        print(f"{result} {test_name}")
    
    passed = sum(1 for _, result in results if result.startswith("✅"))
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 2 tests passed! Semantic matching is working!")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
