from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectModel(BaseModel):
    """Model for project data from knowledge base"""
    title: str
    summary: str
    raw_summary: str
    technologies: Optional[List[str]] = []
    relevance_score: Optional[float] = 0.0
    
    
class ExperienceModel(BaseModel):
    """Model for work experience data"""
    id: int
    company: str
    position: str
    location: str
    duration: Dict[str, str]
    type: str
    status: str
    description: List[str]
    technologies: Optional[List[str]] = []
    achievements: Optional[List[str]] = []


class SkillModel(BaseModel):
    """Model for skills data"""
    name: str
    proficiency: str
    years_experience: str
    context: List[str]


class JobAnalysisModel(BaseModel):
    """Model for job description analysis results"""
    required_skills: List[str]
    preferred_skills: List[str]
    keywords: List[str]
    industry_focus: Optional[str] = None
    experience_level: Optional[str] = None
    job_title: Optional[str] = None
    technologies: List[str]
    company_name: Optional[str] = None


class ResumeGenerationRequest(BaseModel):
    """Model for resume generation request"""
    job_description: str
    user_preferences: Optional[Dict[str, Any]] = {}
    max_projects: int = Field(default=4, ge=1, le=6)
    target_length: str = Field(default="single-page", pattern="^(single-page|two-page)$")


class ResumeGenerationResponse(BaseModel):
    """Model for resume generation response"""
    resume_id: str
    pdf_file_path: Optional[str] = None
    latex_file_path: Optional[str] = None
    selected_projects: List[ProjectModel]
    selected_experience: List[ExperienceModel]
    job_analysis: JobAnalysisModel
    ats_score: Optional[Dict[str, Any]] = None
    generation_timestamp: datetime
    status: str = "completed"


class FeedbackRequest(BaseModel):
    """Model for feedback on generated resume"""
    resume_id: str
    feedback: str
    section: Optional[str] = None  # "projects", "experience", "skills", "summary", "all"
    specific_changes: Optional[List[str]] = []


class ResumeContent(BaseModel):
    """Model for structured resume content"""
    personal_info: Dict[str, str]
    professional_summary: str
    experience: List[ExperienceModel]
    projects: List[ProjectModel]
    skills: Dict[str, List[str]]
    education: Dict[str, Any]
    additional_sections: Optional[Dict[str, Any]] = {}
    

class ATSAnalysisModel(BaseModel):
    """Model for ATS optimization analysis"""
    overall_score: float = Field(ge=0, le=100)
    keyword_density: Dict[str, float]
    missing_keywords: List[str]
    recommendations: List[str]
    section_scores: Dict[str, float]
    

class KnowledgeBaseModel(BaseModel):
    """Model for loaded knowledge base"""
    projects: List[ProjectModel]
    experience: List[ExperienceModel]
    skills: Dict[str, List[SkillModel]]
    profile_summary: Dict[str, Any]
    load_timestamp: datetime
