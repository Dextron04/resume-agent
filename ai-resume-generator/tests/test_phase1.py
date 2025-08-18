import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch

from app.services.resume_agent import ResumeAIAgent
from app.models import ProjectModel, ExperienceModel, JobAnalysisModel


class TestPhase1:
    """Phase 1 Tests: Core Foundation & Job Analysis Engine"""
    
    @pytest.fixture
    def setup_test_knowledge_base(self):
        """Create a temporary test knowledge base"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create github_projects directory
            projects_dir = os.path.join(temp_dir, "github_projects")
            os.makedirs(projects_dir)
            
            # Create sample project files
            test_projects = [
                {
                    "metadata": {
                        "project_number": 1,
                        "total_projects": 25,
                        "user_name": "Test User"
                    },
                    "project": {
                        "title": "ConnectX",
                        "summary": "**Project Overview:**\nConnectX is a real-time chat application built with React and Node.js.\n\n**Technologies Used:**\nReact, Node.js, Socket.io, PostgreSQL",
                        "raw_summary": "ConnectX is a real-time chat application built with React and Node.js. Technologies: React, Node.js, Socket.io, PostgreSQL"
                    }
                },
                {
                    "metadata": {
                        "project_number": 2,
                        "total_projects": 25,
                        "user_name": "Test User"
                    },
                    "project": {
                        "title": "Portfolio Website",
                        "summary": "**Project Overview:**\nPersonal portfolio website.\n\n**Technologies Used:**\nNext.js, TypeScript, Tailwind CSS",
                        "raw_summary": "Personal portfolio website. Technologies: Next.js, TypeScript, Tailwind CSS"
                    }
                }
            ]
            
            # Write project files
            for i, project in enumerate(test_projects):
                filename = f"{i+1:02d}_test_project_{i+1}.json"
                filepath = os.path.join(projects_dir, filename)
                with open(filepath, 'w') as f:
                    json.dump(project, f)
            
            # Create work_experience directory and file
            work_exp_dir = os.path.join(temp_dir, "work_experience")
            os.makedirs(work_exp_dir)
            
            test_experience = {
                "work_experience": {
                    "positions": [
                        {
                            "id": 1,
                            "company": "Test Company",
                            "position": "Software Engineer Intern",
                            "location": "San Francisco, CA",
                            "duration": {"start": "June 2025", "end": "Present"},
                            "type": "internship",
                            "status": "current",
                            "description": ["Built web applications", "Used React and Node.js"],
                            "technologies": ["React", "Node.js"],
                            "achievements": ["Delivered project on time"]
                        }
                    ]
                }
            }
            
            with open(os.path.join(work_exp_dir, "work_experience.json"), 'w') as f:
                json.dump(test_experience, f)
            
            # Create skills directory and file
            skills_dir = os.path.join(temp_dir, "skills")
            os.makedirs(skills_dir)
            
            test_skills = {
                "skills": {
                    "categories": {
                        "programming_languages": {
                            "skills": [
                                {"name": "Python", "proficiency": "Advanced"},
                                {"name": "JavaScript", "proficiency": "Advanced"}
                            ]
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
            
            yield temp_dir
    
    def test_knowledge_base_loading(self, setup_test_knowledge_base):
        """Test that knowledge base loads correctly"""
        temp_dir = setup_test_knowledge_base
        
        # Mock Anthropic client to avoid API calls in tests
        with patch('anthropic.Anthropic'):
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
            
            # Test projects loading
            projects = agent.knowledge_base.projects
            assert len(projects) >= 2
            assert any(p.title == "ConnectX" for p in projects)
            assert any(p.title == "Portfolio Website" for p in projects)
            
            # Test experience loading
            experience = agent.knowledge_base.experience
            assert len(experience) >= 1
            assert any(exp.company == "Test Company" for exp in experience)
            
            # Test skills loading
            skills = agent.knowledge_base.skills
            assert skills is not None
            assert len(skills.programming_languages) >= 2
    
    def test_tech_extraction(self, setup_test_knowledge_base):
        """Test technology extraction from project summaries"""
        temp_dir = setup_test_knowledge_base
        
        with patch('anthropic.Anthropic'):
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
            
            # Test with various summary formats
            test_cases = [
                {
                    "summary": "**Technologies Used:**\nReact, Node.js, PostgreSQL, Docker",
                    "expected": ["React", "Node.js", "PostgreSQL", "Docker"]
                },
                {
                    "summary": "Built with Next.js and TypeScript. Database: MongoDB",
                    "expected": ["Next.js", "TypeScript", "MongoDB"]
                },
                {
                    "summary": "Technologies: Python, Flask, SQLite",
                    "expected": ["Python", "Flask", "SQLite"]
                }
            ]
            
            for test_case in test_cases:
                technologies = agent.extract_technologies_from_summary(test_case["summary"])
                for expected_tech in test_case["expected"]:
                    assert expected_tech in technologies, f"Expected {expected_tech} in {technologies}"
    
    @patch('anthropic.Anthropic')
    def test_job_analysis_with_mock_anthropic(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test job description analysis with mocked Anthropic"""
        temp_dir = setup_test_knowledge_base
        
        # Mock the Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "required_skills": ["React", "Node.js", "JavaScript"],
            "preferred_skills": ["TypeScript", "Docker"],
            "keywords": ["React", "Node.js", "frontend", "development"],
            "industry_focus": "Technology",
            "experience_level": "Mid-level",
            "job_title": "Frontend Developer",
            "technologies": ["React", "Node.js", "JavaScript"],
            "company_name": "Test Corp"
        })
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
        
        job_desc = "We need a React developer with Node.js experience for frontend development at Test Corp."
        analysis = agent.analyze_job_description(job_desc)
        
        assert isinstance(analysis, JobAnalysisModel)
        assert "React" in analysis.required_skills
        assert "Node.js" in analysis.required_skills
        assert "React" in analysis.keywords
        assert analysis.job_title == "Frontend Developer"
        assert analysis.company_name == "Test Corp"
    
    def test_job_analysis_fallback(self, setup_test_knowledge_base):
        """Test job analysis fallback when Anthropic fails"""
        temp_dir = setup_test_knowledge_base
        
        # Mock Anthropic to raise an exception
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API Error")
            mock_anthropic.return_value = mock_client
            
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
            
            job_desc = "We need a React developer with Node.js and Python experience."
            analysis = agent.analyze_job_description(job_desc)
            
            # Should still return a valid analysis using fallback
            assert isinstance(analysis, JobAnalysisModel)
            # Fallback should extract some basic keywords
            assert len(analysis.keywords) > 0
    
    def test_empty_knowledge_base(self):
        """Test handling of empty or missing knowledge base"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create empty directories
            os.makedirs(os.path.join(temp_dir, "github_projects"))
            os.makedirs(os.path.join(temp_dir, "work_experience"))
            os.makedirs(os.path.join(temp_dir, "skills"))
            
            with patch('anthropic.Anthropic'):
                agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
                
                # Should handle empty knowledge base gracefully
                assert len(agent.knowledge_base.projects) == 0
                assert len(agent.knowledge_base.experience) == 0
                assert len(agent.knowledge_base.skills) == 0
