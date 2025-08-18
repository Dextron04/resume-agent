import os
import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

import anthropic
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.models import (
    ProjectModel, ExperienceModel, SkillModel, JobAnalysisModel,
    ResumeContent, ATSAnalysisModel, KnowledgeBaseModel
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResumeAIAgent:
    """
    Core AI agent for generating tailored resumes from job descriptions
    """
    
    def __init__(self, knowledge_base_path: str, anthropic_api_key: str, load_sentence_model: bool = True):
        """
        Initialize the AI agent with knowledge base and API credentials
        
        Args:
            knowledge_base_path: Path to the knowledge base directory
            anthropic_api_key: Anthropic API key for Claude integration
            load_sentence_model: Whether to load the sentence transformer model immediately
        """
        self.knowledge_base_path = knowledge_base_path
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Initialize sentence transformer for semantic similarity (lazy loading)
        self.sentence_model = None
        self._load_sentence_model = load_sentence_model
        if load_sentence_model:
            self._initialize_sentence_model()
        
        # Load knowledge base
        self.knowledge_base = self.load_knowledge_base()
        
        logger.info("ResumeAIAgent initialized successfully")
    
    def _initialize_sentence_model(self):
        """Initialize the sentence transformer model with progress tracking"""
        if self.sentence_model is None:
            logger.info("Loading sentence transformer model (this may take a few minutes on first run)...")
            try:
                # Set timeout and show progress
                import os
                os.environ['TRANSFORMERS_CACHE'] = os.path.expanduser('~/.cache/huggingface/transformers')
                
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Sentence transformer model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer model: {e}")
                logger.info("Continuing without semantic similarity features...")
                self.sentence_model = None
    
    def get_sentence_model(self):
        """Get the sentence transformer model, initializing if needed"""
        if self.sentence_model is None:
            self._initialize_sentence_model()
        return self.sentence_model
    
    def load_knowledge_base(self) -> KnowledgeBaseModel:
        """
        Load all knowledge base files and return structured data
        
        Returns:
            KnowledgeBaseModel: Structured knowledge base data
        """
        logger.info("Loading knowledge base...")
        
        # Load projects
        projects = self.load_projects()
        
        # Load experience
        experience = self.load_experience()
        
        # Load skills
        skills = self.load_skills()
        
        # Load profile summary
        profile_summary = self.load_profile_summary()
        
        knowledge_base = KnowledgeBaseModel(
            projects=projects,
            experience=experience,
            skills=skills,
            profile_summary=profile_summary,
            load_timestamp=datetime.now()
        )
        
        logger.info(f"Knowledge base loaded: {len(projects)} projects, {len(experience)} experiences")
        return knowledge_base
    
    def load_projects(self) -> List[ProjectModel]:
        """
        Load projects from GitHub projects JSON files
        
        Returns:
            List[ProjectModel]: List of project models
        """
        projects = []
        projects_dir = os.path.join(self.knowledge_base_path, "github_projects")
        
        if not os.path.exists(projects_dir):
            logger.warning(f"Projects directory not found: {projects_dir}")
            return projects
        
        # Get all JSON files in projects directory
        json_files = [f for f in os.listdir(projects_dir) if f.endswith('.json') and not f.startswith('00_index')]
        
        for file in sorted(json_files):
            file_path = os.path.join(projects_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if 'project' in data:
                    project_data = data['project']
                    
                    # Extract technologies from summary
                    technologies = self.extract_technologies_from_summary(project_data.get('summary', ''))
                    
                    project = ProjectModel(
                        title=project_data.get('title', ''),
                        summary=project_data.get('summary', ''),
                        raw_summary=project_data.get('raw_summary', ''),
                        technologies=technologies
                    )
                    projects.append(project)
                    
            except Exception as e:
                logger.error(f"Error loading project file {file}: {e}")
                continue
        
        return projects
    
    def load_experience(self) -> List[ExperienceModel]:
        """
        Load work experience from JSON files
        
        Returns:
            List[ExperienceModel]: List of experience models
        """
        experience = []
        experience_path = os.path.join(self.knowledge_base_path, "work_experience", "work_experience.json")
        
        if not os.path.exists(experience_path):
            logger.warning(f"Experience file not found: {experience_path}")
            return experience
        
        try:
            with open(experience_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            positions = data.get('work_experience', {}).get('positions', [])
            
            for pos in positions:
                exp = ExperienceModel(
                    id=pos.get('id', 0),
                    company=pos.get('company', ''),
                    position=pos.get('position', ''),
                    location=pos.get('location', ''),
                    duration=pos.get('duration', {}),
                    type=pos.get('type', ''),
                    status=pos.get('status', ''),
                    description=pos.get('description', []),
                    technologies=pos.get('technologies', []),
                    achievements=pos.get('achievements', [])
                )
                experience.append(exp)
                
        except Exception as e:
            logger.error(f"Error loading experience: {e}")
        
        return experience
    
    def load_skills(self) -> Dict[str, List[SkillModel]]:
        """
        Load skills from JSON files
        
        Returns:
            Dict[str, List[SkillModel]]: Skills organized by category
        """
        skills = {}
        skills_path = os.path.join(self.knowledge_base_path, "skills", "skills.json")
        
        if not os.path.exists(skills_path):
            logger.warning(f"Skills file not found: {skills_path}")
            return skills
        
        try:
            with open(skills_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            categories = data.get('skills', {}).get('categories', {})
            
            for category_key, category_data in categories.items():
                category_skills = []
                for skill_data in category_data.get('skills', []):
                    skill = SkillModel(
                        name=skill_data.get('name', ''),
                        proficiency=skill_data.get('proficiency', ''),
                        years_experience=skill_data.get('years_experience', ''),
                        context=skill_data.get('context', [])
                    )
                    category_skills.append(skill)
                    
                skills[category_key] = category_skills
                
        except Exception as e:
            logger.error(f"Error loading skills: {e}")
        
        return skills
    
    def load_profile_summary(self) -> Dict[str, Any]:
        """
        Load profile summary from JSON file
        
        Returns:
            Dict[str, Any]: Profile summary data
        """
        summary_path = os.path.join(self.knowledge_base_path, "profile_summary.json")
        
        if not os.path.exists(summary_path):
            logger.warning(f"Profile summary file not found: {summary_path}")
            return {}
        
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('profile_summary', {})
        except Exception as e:
            logger.error(f"Error loading profile summary: {e}")
            return {}
    
    def extract_technologies_from_summary(self, summary: str) -> List[str]:
        """
        Extract technologies from project summary using regex patterns
        
        Args:
            summary: Project summary text
            
        Returns:
            List[str]: List of extracted technologies
        """
        technologies = []
        
        # Common patterns for technology extraction
        tech_patterns = [
            r"Technologies Used:\s*([^\n]+)",     # "Technologies Used: X, Y, Z"
            r"Technologies:\s*([^\n]+)",          # "Technologies: X, Y, Z"
            r"Built with\s+([^\n.]+)",            # "Built with X, Y, Z"
            r"using\s+([A-Z][a-z]+(?:\.[a-z]+)?(?:,\s*[A-Z][a-z]+(?:\.[a-z]+)?)*)",  # "using React, Node.js"
            r"Database:\s*([^\n.]+)",             # "Database: MongoDB"
        ]
        
        # Known technology keywords to look for
        known_techs = [
            "React", "Node.js", "Python", "Java", "JavaScript", "TypeScript",
            "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Docker", "AWS", "Next.js",
            "Spring Boot", "Django", "Flask", "Express", "Vue.js", "Angular",
            "Redis", "Kubernetes", "Git", "GitHub", "REST", "GraphQL",
            "Socket.io", "JWT", "OAuth", "TensorFlow", "PyTorch", "Scikit-learn",
            "HTML", "CSS", "SASS", "Tailwind", "Bootstrap", "Material-UI",
            "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin",
            "Laravel", "Symfony", "Rails", "ASP.NET", "Nginx", "Apache",
            "Linux", "Ubuntu", "CentOS", "Windows", "macOS", "Prisma",
            "Sequelize", "Mongoose", "Hibernate", "JPA", "SQLAlchemy"
        ]
        
        # Try pattern matching first
        for pattern in tech_patterns:
            matches = re.findall(pattern, summary, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters
                techs = re.split(r'[,;&]', match)
                for tech in techs:
                    tech = tech.strip()
                    if tech:
                        technologies.append(tech)
        
        # Look for known technologies in the text
        for tech in known_techs:
            if re.search(r'\b' + re.escape(tech) + r'\b', summary, re.IGNORECASE):
                if tech not in technologies:
                    technologies.append(tech)
        
        # Clean and deduplicate
        technologies = list(set([tech.strip() for tech in technologies if tech.strip()]))
        
        return technologies
    
    def analyze_job_description(self, job_desc: str) -> JobAnalysisModel:
        """
        Analyze job description to extract keywords and requirements
        
        Args:
            job_desc: Job description text
            
        Returns:
            JobAnalysisModel: Analysis results
        """
        logger.info("Analyzing job description...")
        
        try:
            # Use Claude to analyze the job description
            prompt = f"""
            Analyze the following job description and extract key information:
            
            Job Description:
            {job_desc}
            
            Please extract and format as JSON:
            1. required_skills: List of required technical skills
            2. preferred_skills: List of preferred/nice-to-have skills
            3. keywords: Important keywords for ATS optimization
            4. industry_focus: Industry or domain focus
            5. experience_level: Required experience level
            6. job_title: Job title
            7. technologies: Specific technologies mentioned
            8. company_name: Company name if mentioned
            
            Return only valid JSON format.
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.1,
                system="You are an expert at analyzing job descriptions for resume optimization.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            analysis_text = response.content[0].text.strip()
            
            # Try to parse JSON response
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Fallback to basic extraction if JSON parsing fails
                logger.warning("Failed to parse Claude JSON response, using fallback extraction")
                analysis_data = self._fallback_job_analysis(job_desc)
            
            job_analysis = JobAnalysisModel(
                required_skills=analysis_data.get('required_skills', []),
                preferred_skills=analysis_data.get('preferred_skills', []),
                keywords=analysis_data.get('keywords', []),
                industry_focus=analysis_data.get('industry_focus'),
                experience_level=analysis_data.get('experience_level'),
                job_title=analysis_data.get('job_title'),
                technologies=analysis_data.get('technologies', []),
                company_name=analysis_data.get('company_name')
            )
            
            logger.info(f"Job analysis completed: {len(job_analysis.keywords)} keywords identified")
            return job_analysis
            
        except Exception as e:
            logger.error(f"Error in job analysis: {e}")
            # Return fallback analysis
            return JobAnalysisModel(
                required_skills=self._extract_skills_fallback(job_desc),
                preferred_skills=[],
                keywords=self._extract_keywords_fallback(job_desc),
                technologies=self._extract_technologies_fallback(job_desc),
                industry_focus="Technology",
                experience_level="Mid-level"
            )
    
    def _fallback_job_analysis(self, job_desc: str) -> Dict[str, Any]:
        """
        Fallback job analysis using regex patterns
        
        Args:
            job_desc: Job description text
            
        Returns:
            Dict[str, Any]: Basic analysis results
        """
        # Simple regex-based extraction
        common_skills = [
            "Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Docker",
            "PostgreSQL", "MySQL", "MongoDB", "Git", "Linux", "Kubernetes",
            "Spring Boot", "Django", "Flask", "Express", "Vue.js", "Angular"
        ]
        
        found_skills = []
        keywords = []
        
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', job_desc, re.IGNORECASE):
                found_skills.append(skill)
                keywords.append(skill)
        
        # Extract additional keywords (capitalized words)
        additional_keywords = re.findall(r'\b[A-Z][a-z]+\b', job_desc)
        keywords.extend(additional_keywords[:10])  # Limit to 10 additional keywords
        
        return {
            "required_skills": found_skills[:8],
            "preferred_skills": [],
            "keywords": list(set(keywords)),
            "technologies": found_skills,
            "industry_focus": "Technology",
            "experience_level": "Mid-level",
            "job_title": "Software Engineer",
            "company_name": None
        }
    
    def _extract_skills_fallback(self, text: str) -> List[str]:
        """Basic skill extraction fallback"""
        skills = []
        skill_patterns = [
            "Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Docker"
        ]
        
        for skill in skill_patterns:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                skills.append(skill)
        
        return skills
    
    def _extract_keywords_fallback(self, text: str) -> List[str]:
        """Basic keyword extraction fallback"""
        # Extract capitalized words as potential keywords
        keywords = re.findall(r'\b[A-Z][a-z]+\b', text)
        return list(set(keywords))[:15]  # Limit to 15 keywords
    
    def _extract_technologies_fallback(self, text: str) -> List[str]:
        """Basic technology extraction fallback"""
        return self._extract_skills_fallback(text)  # Same as skills for now
