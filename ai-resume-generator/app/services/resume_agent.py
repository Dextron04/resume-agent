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
    
    # ============================================================================
    # PHASE 2: SEMANTIC MATCHING & INTELLIGENT PROJECT SELECTION
    # ============================================================================
    
    def calculate_project_relevance(self, job_analysis: JobAnalysisModel, max_projects: int = 4) -> List[Tuple[ProjectModel, float]]:
        """
        Calculate relevance scores for all projects based on job requirements
        
        Args:
            job_analysis: Analyzed job requirements
            max_projects: Maximum number of projects to return
            
        Returns:
            List[Tuple[ProjectModel, float]]: Projects with relevance scores (0-1)
        """
        logger.info(f"Calculating project relevance for {len(self.knowledge_base.projects)} projects...")
        
        if not self.knowledge_base.projects:
            logger.warning("No projects found in knowledge base")
            return []
        
        # Combine job requirements for semantic matching
        job_requirements = self._combine_job_requirements(job_analysis)
        
        relevance_scores = []
        
        for project in self.knowledge_base.projects:
            try:
                # Calculate semantic similarity score
                semantic_score = self._calculate_semantic_similarity(job_requirements, project.summary)
                
                # Calculate technology overlap score
                tech_overlap_score = self._calculate_technology_overlap(job_analysis.technologies, project.technologies)
                
                # Calculate keyword match score
                keyword_score = self._calculate_keyword_match(job_analysis.keywords, project.summary)
                
                # Combine scores with weights
                combined_score = (
                    semantic_score * 0.5 +      # Semantic similarity (50%)
                    tech_overlap_score * 0.3 +  # Technology overlap (30%)
                    keyword_score * 0.2          # Keyword matching (20%)
                )
                
                # Boost score if project has many required skills
                required_skills_boost = self._calculate_required_skills_boost(job_analysis.required_skills, project.technologies)
                combined_score += required_skills_boost * 0.1
                
                # Ensure score is between 0 and 1
                combined_score = min(1.0, max(0.0, combined_score))
                
                relevance_scores.append((project, combined_score))
                
                logger.debug(f"Project '{project.title}': semantic={semantic_score:.3f}, tech={tech_overlap_score:.3f}, "
                           f"keyword={keyword_score:.3f}, combined={combined_score:.3f}")
                
            except Exception as e:
                logger.error(f"Error calculating relevance for project '{project.title}': {e}")
                relevance_scores.append((project, 0.0))
        
        # Sort by relevance score (highest first) and return top projects
        sorted_projects = sorted(relevance_scores, key=lambda x: x[1], reverse=True)
        top_projects = sorted_projects[:max_projects]
        
        logger.info(f"Top {len(top_projects)} projects selected with scores: "
                   f"{[f'{p[0].title}({p[1]:.3f})' for p in top_projects]}")
        
        return top_projects
    
    def calculate_experience_relevance(self, job_analysis: JobAnalysisModel) -> List[Tuple[ExperienceModel, float]]:
        """
        Calculate relevance scores for work experiences based on job requirements
        
        Args:
            job_analysis: Analyzed job requirements
            
        Returns:
            List[Tuple[ExperienceModel, float]]: Experiences with relevance scores
        """
        logger.info(f"Calculating experience relevance for {len(self.knowledge_base.experience)} experiences...")
        
        if not self.knowledge_base.experience:
            logger.warning("No work experience found in knowledge base")
            return []
        
        job_requirements = self._combine_job_requirements(job_analysis)
        relevance_scores = []
        
        for experience in self.knowledge_base.experience:
            try:
                # Combine experience description for analysis
                exp_text = " ".join(experience.description + experience.achievements)
                
                # Calculate semantic similarity
                semantic_score = self._calculate_semantic_similarity(job_requirements, exp_text)
                
                # Calculate technology overlap
                tech_overlap_score = self._calculate_technology_overlap(job_analysis.technologies, experience.technologies)
                
                # Calculate seniority match (current positions get higher scores)
                seniority_score = 1.0 if experience.status == "current" else 0.7
                
                # Combine scores
                combined_score = (
                    semantic_score * 0.4 +      # Semantic similarity (40%)
                    tech_overlap_score * 0.4 +  # Technology overlap (40%)
                    seniority_score * 0.2        # Seniority/recency (20%)
                )
                
                combined_score = min(1.0, max(0.0, combined_score))
                relevance_scores.append((experience, combined_score))
                
                logger.debug(f"Experience '{experience.position} at {experience.company}': "
                           f"semantic={semantic_score:.3f}, tech={tech_overlap_score:.3f}, "
                           f"seniority={seniority_score:.3f}, combined={combined_score:.3f}")
                
            except Exception as e:
                logger.error(f"Error calculating relevance for experience '{experience.position}': {e}")
                relevance_scores.append((experience, 0.0))
        
        # Sort by relevance score (highest first)
        sorted_experiences = sorted(relevance_scores, key=lambda x: x[1], reverse=True)
        
        logger.info(f"Experience relevance calculated: "
                   f"{[f'{e[0].position}({e[1]:.3f})' for e in sorted_experiences]}")
        
        return sorted_experiences
    
    def generate_tailored_content(self, job_analysis: JobAnalysisModel, max_projects: int = 4) -> Dict[str, Any]:
        """
        Generate tailored resume content based on job analysis
        
        Args:
            job_analysis: Analyzed job requirements
            max_projects: Maximum number of projects to include
            
        Returns:
            Dict[str, Any]: Tailored content with selected projects and experiences
        """
        logger.info("Generating tailored resume content...")
        
        # Get most relevant projects
        relevant_projects = self.calculate_project_relevance(job_analysis, max_projects)
        
        # Get most relevant experiences
        relevant_experiences = self.calculate_experience_relevance(job_analysis)
        
        # Select top skills based on job requirements
        relevant_skills = self._select_relevant_skills(job_analysis)
        
        # Generate optimized summary/objective
        optimized_summary = self._generate_optimized_summary(job_analysis)
        
        tailored_content = {
            "job_analysis": job_analysis.dict(),
            "selected_projects": [
                {
                    "project": project.dict(),
                    "relevance_score": score,
                    "match_reasons": self._explain_project_match(job_analysis, project)
                }
                for project, score in relevant_projects
            ],
            "selected_experiences": [
                {
                    "experience": exp.dict(),
                    "relevance_score": score,
                    "match_reasons": self._explain_experience_match(job_analysis, exp)
                }
                for exp, score in relevant_experiences[:3]  # Top 3 experiences
            ],
            "relevant_skills": relevant_skills,
            "optimized_summary": optimized_summary,
            "optimization_metadata": {
                "total_projects_available": len(self.knowledge_base.projects),
                "total_experiences_available": len(self.knowledge_base.experience),
                "projects_selected": len(relevant_projects),
                "experiences_selected": min(3, len(relevant_experiences)),
                "generation_timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"Tailored content generated: {len(relevant_projects)} projects, "
                   f"{min(3, len(relevant_experiences))} experiences selected")
        
        return tailored_content
    
    def _combine_job_requirements(self, job_analysis: JobAnalysisModel) -> str:
        """Combine all job requirements into a single text for semantic analysis"""
        requirements = []
        
        if job_analysis.required_skills:
            requirements.append("Required skills: " + ", ".join(job_analysis.required_skills))
        
        if job_analysis.preferred_skills:
            requirements.append("Preferred skills: " + ", ".join(job_analysis.preferred_skills))
        
        if job_analysis.keywords:
            requirements.append("Keywords: " + ", ".join(job_analysis.keywords))
        
        if job_analysis.technologies:
            requirements.append("Technologies: " + ", ".join(job_analysis.technologies))
        
        if job_analysis.industry_focus:
            requirements.append(f"Industry: {job_analysis.industry_focus}")
        
        if job_analysis.job_title:
            requirements.append(f"Role: {job_analysis.job_title}")
        
        return ". ".join(requirements)
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts using sentence transformers
        
        Args:
            text1: First text (job requirements)
            text2: Second text (project/experience description)
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            model = self.get_sentence_model()
            if model is None:
                logger.warning("Sentence model not available, using fallback similarity")
                return self._fallback_similarity(text1, text2)
            
            # Encode both texts
            embeddings = model.encode([text1, text2])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity([embeddings[0]], [embeddings[1]])
            similarity_score = similarity_matrix[0][0]
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, float(similarity_score)))
            
        except Exception as e:
            logger.warning(f"Error calculating semantic similarity: {e}")
            return self._fallback_similarity(text1, text2)
    
    def _calculate_technology_overlap(self, job_techs: List[str], project_techs: List[str]) -> float:
        """
        Calculate overlap between job technologies and project technologies
        
        Args:
            job_techs: Technologies mentioned in job description
            project_techs: Technologies used in project
            
        Returns:
            float: Overlap score between 0 and 1
        """
        if not job_techs:
            return 0.0
        
        job_techs_lower = [tech.lower() for tech in job_techs]
        project_techs_lower = [tech.lower() for tech in project_techs]
        
        # Calculate intersection
        overlap = set(job_techs_lower) & set(project_techs_lower)
        
        # Return Jaccard similarity (intersection / union)
        union = set(job_techs_lower) | set(project_techs_lower)
        
        if not union:
            return 0.0
        
        return len(overlap) / len(union)
    
    def _calculate_keyword_match(self, keywords: List[str], text: str) -> float:
        """
        Calculate how many keywords from job description appear in text
        
        Args:
            keywords: Keywords from job analysis
            text: Text to search in
            
        Returns:
            float: Match score between 0 and 1
        """
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matched_keywords = 0
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched_keywords += 1
        
        return matched_keywords / len(keywords)
    
    def _calculate_required_skills_boost(self, required_skills: List[str], project_techs: List[str]) -> float:
        """
        Calculate boost score based on how many required skills the project demonstrates
        
        Args:
            required_skills: Required skills from job
            project_techs: Technologies in project
            
        Returns:
            float: Boost score (0 to 1)
        """
        if not required_skills:
            return 0.0
        
        required_lower = [skill.lower() for skill in required_skills]
        project_lower = [tech.lower() for tech in project_techs]
        
        matched_skills = sum(1 for skill in required_lower if skill in project_lower)
        
        return matched_skills / len(required_skills)
    
    def _fallback_similarity(self, text1: str, text2: str) -> float:
        """
        Fallback similarity calculation using simple word overlap
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Basic similarity score
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _select_relevant_skills(self, job_analysis: JobAnalysisModel) -> Dict[str, List[str]]:
        """
        Select and prioritize skills based on job requirements
        
        Args:
            job_analysis: Job analysis results
            
        Returns:
            Dict[str, List[str]]: Categorized relevant skills
        """
        relevant_skills = {}
        job_techs_lower = [tech.lower() for tech in job_analysis.technologies + job_analysis.required_skills]
        
        for category, skills in self.knowledge_base.skills.items():
            category_relevant = []
            
            for skill in skills:
                skill_name_lower = skill.name.lower()
                
                # Check if skill matches job requirements
                if any(tech in skill_name_lower or skill_name_lower in tech for tech in job_techs_lower):
                    category_relevant.append(skill.name)
            
            if category_relevant:
                relevant_skills[category] = category_relevant
        
        return relevant_skills
    
    def _generate_optimized_summary(self, job_analysis: JobAnalysisModel) -> str:
        """
        Generate an optimized professional summary based on job requirements
        
        Args:
            job_analysis: Job analysis results
            
        Returns:
            str: Optimized professional summary
        """
        profile = self.knowledge_base.profile_summary.get('personal_info', {})
        name = profile.get('name', 'Software Engineer')
        title = profile.get('title', job_analysis.job_title or 'Software Engineer')
        
        # Key technologies to highlight
        key_techs = job_analysis.technologies[:5]  # Top 5 technologies
        tech_string = ", ".join(key_techs) if key_techs else "modern technologies"
        
        # Experience level
        exp_level = job_analysis.experience_level or "experienced"
        
        summary = (f"{exp_level} {title} with expertise in {tech_string}. "
                  f"Proven track record of delivering high-quality software solutions "
                  f"and collaborating effectively in agile development environments.")
        
        return summary
    
    def _explain_project_match(self, job_analysis: JobAnalysisModel, project: ProjectModel) -> List[str]:
        """
        Generate explanations for why a project matches the job requirements
        
        Args:
            job_analysis: Job analysis results
            project: Project model
            
        Returns:
            List[str]: List of match reasons
        """
        reasons = []
        
        # Technology matches
        job_techs_lower = [tech.lower() for tech in job_analysis.technologies]
        project_techs_lower = [tech.lower() for tech in project.technologies]
        tech_matches = [tech for tech in project.technologies if tech.lower() in job_techs_lower]
        
        if tech_matches:
            reasons.append(f"Uses required technologies: {', '.join(tech_matches)}")
        
        # Keyword matches
        keyword_matches = [kw for kw in job_analysis.keywords if kw.lower() in project.summary.lower()]
        if keyword_matches:
            reasons.append(f"Contains relevant keywords: {', '.join(keyword_matches[:3])}")
        
        # Domain relevance
        if job_analysis.industry_focus and job_analysis.industry_focus.lower() in project.summary.lower():
            reasons.append(f"Relevant to {job_analysis.industry_focus} industry")
        
        return reasons
    
    def _explain_experience_match(self, job_analysis: JobAnalysisModel, experience: ExperienceModel) -> List[str]:
        """
        Generate explanations for why an experience matches the job requirements
        
        Args:
            job_analysis: Job analysis results
            experience: Experience model
            
        Returns:
            List[str]: List of match reasons
        """
        reasons = []
        
        # Technology matches
        job_techs_lower = [tech.lower() for tech in job_analysis.technologies]
        exp_techs_lower = [tech.lower() for tech in experience.technologies]
        tech_matches = [tech for tech in experience.technologies if tech.lower() in job_techs_lower]
        
        if tech_matches:
            reasons.append(f"Experience with: {', '.join(tech_matches)}")
        
        # Position relevance
        if job_analysis.job_title:
            if job_analysis.job_title.lower() in experience.position.lower():
                reasons.append(f"Similar role: {experience.position}")
        
        # Current position boost
        if experience.status == "current":
            reasons.append("Current position (most recent experience)")
        
        return reasons
