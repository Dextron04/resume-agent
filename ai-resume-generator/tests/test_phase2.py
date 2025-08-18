import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.resume_agent import ResumeAIAgent
from app.models import ProjectModel, ExperienceModel, JobAnalysisModel


class TestPhase2:
    """Phase 2 Tests: Semantic Matching & Intelligent Project Selection"""
    
    @pytest.fixture
    def setup_test_knowledge_base(self):
        """Create a comprehensive test knowledge base for Phase 2"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create github_projects directory with diverse projects
            projects_dir = os.path.join(temp_dir, "github_projects")
            os.makedirs(projects_dir)
            
            # Create diverse test projects
            test_projects = [
                {
                    "metadata": {"project_number": 1, "total_projects": 25, "user_name": "Test User"},
                    "project": {
                        "title": "E-commerce Platform",
                        "summary": "**Project Overview:**\nFull-stack e-commerce platform built with React and Node.js. Features include user authentication, payment processing, inventory management, and order tracking.\n\n**Technologies Used:**\nReact, Node.js, Express, PostgreSQL, Stripe, JWT, Docker",
                        "raw_summary": "E-commerce platform with React, Node.js, PostgreSQL"
                    }
                },
                {
                    "metadata": {"project_number": 2, "total_projects": 25, "user_name": "Test User"},
                    "project": {
                        "title": "ML Data Pipeline",
                        "summary": "**Project Overview:**\nMachine learning data pipeline for processing large datasets. Implemented ETL processes, model training, and automated deployment.\n\n**Technologies Used:**\nPython, Apache Spark, TensorFlow, Kubernetes, Apache Kafka, PostgreSQL",
                        "raw_summary": "ML pipeline with Python, Spark, TensorFlow"
                    }
                },
                {
                    "metadata": {"project_number": 3, "total_projects": 25, "user_name": "Test User"},
                    "project": {
                        "title": "Mobile Fitness App",
                        "summary": "**Project Overview:**\nCross-platform mobile fitness tracking application. Features workout planning, progress tracking, and social sharing.\n\n**Technologies Used:**\nReact Native, Firebase, Node.js, MongoDB, Redux",
                        "raw_summary": "Mobile app with React Native, Firebase"
                    }
                },
                {
                    "metadata": {"project_number": 4, "total_projects": 25, "user_name": "Test User"},
                    "project": {
                        "title": "DevOps Automation Tools",
                        "summary": "**Project Overview:**\nAutomated CI/CD pipeline and infrastructure management tools. Streamlined deployment processes and monitoring.\n\n**Technologies Used:**\nDocker, Kubernetes, Jenkins, Terraform, AWS, Prometheus, Grafana",
                        "raw_summary": "DevOps tools with Docker, Kubernetes, AWS"
                    }
                }
            ]
            
            # Write project files
            for i, project in enumerate(test_projects):
                with open(os.path.join(projects_dir, f"{i+1:02d}_project.json"), 'w') as f:
                    json.dump(project, f)
            
            # Create work_experience directory
            work_exp_dir = os.path.join(temp_dir, "work_experience")
            os.makedirs(work_exp_dir)
            
            test_experience = {
                "work_experience": {
                    "positions": [
                        {
                            "id": 1,
                            "company": "TechCorp Inc",
                            "position": "Full Stack Developer",
                            "location": "San Francisco, CA",
                            "duration": {"start": "January 2024", "end": "Present"},
                            "type": "full-time",
                            "status": "current",
                            "description": [
                                "Developed responsive web applications using React and Node.js",
                                "Implemented RESTful APIs and database optimizations",
                                "Collaborated with cross-functional teams in agile environment"
                            ],
                            "technologies": ["React", "Node.js", "PostgreSQL", "Docker", "AWS"],
                            "achievements": ["Increased application performance by 40%", "Led team of 3 developers"]
                        },
                        {
                            "id": 2,
                            "company": "DataScience LLC",
                            "position": "Machine Learning Engineer",
                            "location": "New York, NY",
                            "duration": {"start": "June 2023", "end": "December 2023"},
                            "type": "internship",
                            "status": "completed",
                            "description": [
                                "Built machine learning models for predictive analytics",
                                "Processed large datasets using Python and Spark",
                                "Deployed models using Kubernetes and MLOps practices"
                            ],
                            "technologies": ["Python", "TensorFlow", "Apache Spark", "Kubernetes", "MLFlow"],
                            "achievements": ["Improved model accuracy by 25%", "Automated data pipeline"]
                        }
                    ]
                }
            }
            
            with open(os.path.join(work_exp_dir, "work_experience.json"), 'w') as f:
                json.dump(test_experience, f)
            
            # Create skills directory
            skills_dir = os.path.join(temp_dir, "skills")
            os.makedirs(skills_dir)
            
            test_skills = {
                "skills": {
                    "categories": {
                        "programming_languages": {
                            "skills": [
                                {"name": "Python", "proficiency": "Expert", "years_experience": "5+"},
                                {"name": "JavaScript", "proficiency": "Expert", "years_experience": "4+"},
                                {"name": "Java", "proficiency": "Intermediate", "years_experience": "2+"}
                            ]
                        },
                        "frontend_frameworks": {
                            "skills": [
                                {"name": "React", "proficiency": "Expert", "years_experience": "3+"},
                                {"name": "React Native", "proficiency": "Intermediate", "years_experience": "1+"}
                            ]
                        },
                        "backend_frameworks": {
                            "skills": [
                                {"name": "Node.js", "proficiency": "Expert", "years_experience": "3+"},
                                {"name": "Express", "proficiency": "Expert", "years_experience": "3+"}
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
                        "title": "Full Stack Developer"
                    }
                }
            }
            
            with open(os.path.join(temp_dir, "profile_summary.json"), 'w') as f:
                json.dump(profile_summary, f)
            
            yield temp_dir
    
    @patch('anthropic.Anthropic')
    def test_semantic_similarity_calculation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test semantic similarity calculation between job requirements and projects"""
        temp_dir = setup_test_knowledge_base
        
        # Mock sentence transformer
        mock_model = MagicMock()
        mock_embeddings = np.array([[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]])  # Similar vectors
        mock_model.encode.return_value = mock_embeddings
        
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_model):
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=True)
            
            # Test semantic similarity calculation
            similarity = agent._calculate_semantic_similarity(
                "React developer with Node.js experience",
                "Full-stack e-commerce platform built with React and Node.js"
            )
            
            assert isinstance(similarity, float)
            assert 0.0 <= similarity <= 1.0
            mock_model.encode.assert_called_once()
    
    @patch('anthropic.Anthropic')
    def test_technology_overlap_calculation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test technology overlap scoring"""
        temp_dir = setup_test_knowledge_base
        
        agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
        
        # Test perfect overlap
        overlap = agent._calculate_technology_overlap(
            ["React", "Node.js", "PostgreSQL"],
            ["React", "Node.js", "PostgreSQL"]
        )
        assert overlap == 1.0
        
        # Test partial overlap
        overlap = agent._calculate_technology_overlap(
            ["React", "Node.js", "MongoDB"],
            ["React", "PostgreSQL", "Docker"]
        )
        expected = 1 / 5  # 1 common (React) out of 5 total unique technologies
        assert abs(overlap - expected) < 0.01
        
        # Test no overlap
        overlap = agent._calculate_technology_overlap(
            ["React", "Vue.js"],
            ["Python", "Django"]
        )
        assert overlap == 0.0
    
    @patch('anthropic.Anthropic')
    def test_project_relevance_calculation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test project relevance scoring with real job analysis"""
        temp_dir = setup_test_knowledge_base
        
        # Mock Anthropic response for job analysis
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "required_skills": ["React", "Node.js", "PostgreSQL"],
            "preferred_skills": ["Docker", "AWS"],
            "keywords": ["full-stack", "web application", "e-commerce"],
            "technologies": ["React", "Node.js", "PostgreSQL", "Docker", "AWS"],
            "industry_focus": "Technology",
            "experience_level": "Mid-level",
            "job_title": "Full Stack Developer",
            "company_name": "TechStartup"
        }))]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        # Mock sentence transformer for consistent results
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.8, 0.2], [0.7, 0.3], [0.3, 0.7], [0.2, 0.8]])
        
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_model):
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=True)
            
            # Analyze job description
            job_analysis = agent.analyze_job_description(
                "We need a Full Stack Developer with React and Node.js experience to build e-commerce applications"
            )
            
            # Calculate project relevance
            relevant_projects = agent.calculate_project_relevance(job_analysis, max_projects=3)
            
            assert len(relevant_projects) <= 3
            assert len(relevant_projects) > 0
            
            # Check that projects are returned with scores
            for project, score in relevant_projects:
                assert isinstance(project, ProjectModel)
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
            
            # Check that projects are sorted by relevance (highest first)
            scores = [score for _, score in relevant_projects]
            assert scores == sorted(scores, reverse=True)
            
            # E-commerce project should have high relevance due to React/Node.js match
            project_titles = [project.title for project, _ in relevant_projects]
            assert "E-commerce Platform" in project_titles
    
    @patch('anthropic.Anthropic')
    def test_experience_relevance_calculation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test work experience relevance scoring"""
        temp_dir = setup_test_knowledge_base
        
        # Mock job analysis
        job_analysis = JobAnalysisModel(
            required_skills=["React", "Node.js"],
            preferred_skills=["PostgreSQL", "AWS"],
            keywords=["full-stack", "web development"],
            technologies=["React", "Node.js", "PostgreSQL", "AWS"],
            industry_focus="Technology",
            experience_level="Mid-level",
            job_title="Full Stack Developer",
            company_name="TechCorp"
        )
        
        # Mock sentence transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.8, 0.2], [0.6, 0.4]])
        
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_model):
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=True)
            
            # Calculate experience relevance
            relevant_experiences = agent.calculate_experience_relevance(job_analysis)
            
            assert len(relevant_experiences) > 0
            
            # Check that experiences are returned with scores
            for experience, score in relevant_experiences:
                assert isinstance(experience, ExperienceModel)
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
            
            # Current position should get higher score than completed internship
            current_exp = next((exp for exp, score in relevant_experiences if exp.status == "current"), None)
            completed_exp = next((exp for exp, score in relevant_experiences if exp.status == "completed"), None)
            
            if current_exp and completed_exp:
                current_score = next(score for exp, score in relevant_experiences if exp.status == "current")
                completed_score = next(score for exp, score in relevant_experiences if exp.status == "completed")
                
                # Current experience should have higher or equal score
                assert current_score >= completed_score
    
    @patch('anthropic.Anthropic')
    def test_tailored_content_generation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test complete tailored content generation"""
        temp_dir = setup_test_knowledge_base
        
        # Mock Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "required_skills": ["React", "Node.js"],
            "preferred_skills": ["Docker", "AWS"],
            "keywords": ["frontend", "backend", "full-stack"],
            "technologies": ["React", "Node.js", "Docker", "AWS"],
            "industry_focus": "Technology",
            "experience_level": "Mid-level",
            "job_title": "Full Stack Developer",
            "company_name": "TechCorp"
        }))]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        # Mock sentence transformer
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.8] * 384] * 10)  # Consistent high similarity
        
        with patch('sentence_transformers.SentenceTransformer', return_value=mock_model):
            agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=True)
            
            # Mock job analysis
            job_analysis = JobAnalysisModel(
                required_skills=["React", "Node.js"],
                preferred_skills=["Docker", "AWS"],
                keywords=["frontend", "backend", "full-stack"],
                technologies=["React", "Node.js", "Docker", "AWS"],
                industry_focus="Technology",
                experience_level="Mid-level",
                job_title="Full Stack Developer",
                company_name="TechCorp"
            )
            
            # Generate tailored content
            tailored_content = agent.generate_tailored_content(job_analysis, max_projects=3)
            
            # Validate structure
            assert "job_analysis" in tailored_content
            assert "selected_projects" in tailored_content
            assert "selected_experiences" in tailored_content
            assert "relevant_skills" in tailored_content
            assert "optimized_summary" in tailored_content
            assert "optimization_metadata" in tailored_content
            
            # Check selected projects
            selected_projects = tailored_content["selected_projects"]
            assert len(selected_projects) <= 3
            assert len(selected_projects) > 0
            
            for project_entry in selected_projects:
                assert "project" in project_entry
                assert "relevance_score" in project_entry
                assert "match_reasons" in project_entry
                assert isinstance(project_entry["relevance_score"], float)
                assert isinstance(project_entry["match_reasons"], list)
            
            # Check selected experiences
            selected_experiences = tailored_content["selected_experiences"]
            assert len(selected_experiences) <= 3
            
            # Check optimized summary
            optimized_summary = tailored_content["optimized_summary"]
            assert isinstance(optimized_summary, str)
            assert len(optimized_summary) > 0
            
            # Check metadata
            metadata = tailored_content["optimization_metadata"]
            assert "total_projects_available" in metadata
            assert "projects_selected" in metadata
            assert "generation_timestamp" in metadata
    
    @patch('anthropic.Anthropic')
    def test_match_explanation_generation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test generation of match explanations for projects and experiences"""
        temp_dir = setup_test_knowledge_base
        
        agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
        
        # Create test job analysis
        job_analysis = JobAnalysisModel(
            required_skills=["React", "Node.js"],
            preferred_skills=["PostgreSQL"],
            keywords=["e-commerce", "web application"],
            technologies=["React", "Node.js", "PostgreSQL"],
            industry_focus="Technology",
            job_title="Frontend Developer"
        )
        
        # Create test project
        project = ProjectModel(
            title="E-commerce Platform",
            summary="Full-stack e-commerce platform built with React and Node.js for online retail",
            technologies=["React", "Node.js", "PostgreSQL", "Docker"]
        )
        
        # Test project match explanation
        match_reasons = agent._explain_project_match(job_analysis, project)
        
        assert isinstance(match_reasons, list)
        assert len(match_reasons) > 0
        
        # Should mention technology matches
        reasons_text = " ".join(match_reasons).lower()
        assert "react" in reasons_text or "node.js" in reasons_text
    
    @patch('anthropic.Anthropic')
    def test_fallback_similarity_calculation(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test fallback similarity calculation when sentence transformer fails"""
        temp_dir = setup_test_knowledge_base
        
        agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
        
        # Test fallback similarity
        similarity = agent._fallback_similarity(
            "React Node.js developer position",
            "Full-stack application using React and Node.js"
        )
        
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0  # Should have some overlap
    
    @patch('anthropic.Anthropic')
    def test_skills_selection_relevance(self, mock_anthropic_class, setup_test_knowledge_base):
        """Test selection of relevant skills based on job requirements"""
        temp_dir = setup_test_knowledge_base
        
        agent = ResumeAIAgent(temp_dir, "test-api-key", load_sentence_model=False)
        
        # Create job analysis focused on frontend
        job_analysis = JobAnalysisModel(
            required_skills=["React", "JavaScript"],
            preferred_skills=["Node.js"],
            keywords=["frontend", "web"],
            technologies=["React", "JavaScript", "Node.js"],
            job_title="Frontend Developer"
        )
        
        # Select relevant skills
        relevant_skills = agent._select_relevant_skills(job_analysis)
        
        assert isinstance(relevant_skills, dict)
        
        # Should include frontend frameworks since React is required
        if "frontend_frameworks" in relevant_skills:
            assert "React" in relevant_skills["frontend_frameworks"]
