from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any
import os
import logging
from dotenv import load_dotenv

from app.models import ResumeGenerationRequest, ResumeGenerationResponse
from app.services.resume_agent import ResumeAIAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Resume Generator",
    description="AI-powered resume tailoring system that generates ATS-optimized PDF resumes",
    version="1.0.0"
)

# Global agent instance (will be initialized on startup)
resume_agent: ResumeAIAgent = None


@app.on_event("startup")
async def startup_event():
    """Initialize the ResumeAIAgent on startup"""
    global resume_agent
    
    try:
        # Get configuration from environment
        knowledge_base_path = os.getenv("KNOWLEDGE_BASE_PATH", "../knowledge_base")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        # Initialize the agent
        resume_agent = ResumeAIAgent(knowledge_base_path, anthropic_api_key)
        logger.info("Resume AI Agent initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Resume AI Agent: {e}")
        raise


def get_resume_agent() -> ResumeAIAgent:
    """Dependency to get the resume agent"""
    if resume_agent is None:
        raise HTTPException(status_code=503, detail="Resume agent not initialized")
    return resume_agent


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Resume Generator API",
        "version": "1.0.0",
        "status": "ready"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_ready": resume_agent is not None
    }


@app.post("/api/analyze-job", response_model=Dict[str, Any])
async def analyze_job_description(
    request: Dict[str, str],
    agent: ResumeAIAgent = Depends(get_resume_agent)
):
    """
    Analyze a job description and extract keywords and requirements
    """
    try:
        job_description = request.get("job_description", "")
        if not job_description:
            raise HTTPException(status_code=400, detail="job_description is required")
        
        analysis = agent.analyze_job_description(job_description)
        
        return {
            "analysis": analysis.dict(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing job description: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-base/summary")
async def get_knowledge_base_summary(
    agent: ResumeAIAgent = Depends(get_resume_agent)
):
    """
    Get a summary of the loaded knowledge base
    """
    try:
        kb = agent.knowledge_base
        
        return {
            "summary": {
                "total_projects": len(kb.projects),
                "total_experience": len(kb.experience),
                "total_skill_categories": len(kb.skills),
                "load_timestamp": kb.load_timestamp.isoformat()
            },
            "projects": [{"title": p.title, "technologies": p.technologies} for p in kb.projects[:5]],
            "experience": [{"company": e.company, "position": e.position} for e in kb.experience[:3]],
            "skill_categories": list(kb.skills.keys())
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge base summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-tailored-content")
async def generate_tailored_content(
    request: Dict[str, Any],
    agent: ResumeAIAgent = Depends(get_resume_agent)
):
    """
    Phase 2: Generate tailored resume content based on job description
    """
    try:
        job_description = request.get("job_description", "")
        max_projects = request.get("max_projects", 4)
        
        if not job_description:
            raise HTTPException(status_code=400, detail="job_description is required")
        
        # Analyze the job description first
        job_analysis = agent.analyze_job_description(job_description)
        
        # Generate tailored content using Phase 2 functionality
        tailored_content = agent.generate_tailored_content(job_analysis, max_projects)
        
        return {
            "tailored_content": tailored_content,
            "status": "success",
            "phase": "2"
        }
        
    except Exception as e:
        logger.error(f"Error generating tailored content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calculate-project-relevance")
async def calculate_project_relevance(
    request: Dict[str, Any],
    agent: ResumeAIAgent = Depends(get_resume_agent)
):
    """
    Phase 2: Calculate relevance scores for projects based on job requirements
    """
    try:
        job_description = request.get("job_description", "")
        max_projects = request.get("max_projects", 10)
        
        if not job_description:
            raise HTTPException(status_code=400, detail="job_description is required")
        
        # Analyze the job description
        job_analysis = agent.analyze_job_description(job_description)
        
        # Calculate project relevance scores
        relevant_projects = agent.calculate_project_relevance(job_analysis, max_projects)
        
        return {
            "job_analysis": job_analysis.dict(),
            "relevant_projects": [
                {
                    "project": {
                        "title": project.title,
                        "technologies": project.technologies,
                        "summary": project.summary[:200] + "..." if len(project.summary) > 200 else project.summary
                    },
                    "relevance_score": round(score, 3),
                    "match_reasons": agent._explain_project_match(job_analysis, project)
                }
                for project, score in relevant_projects
            ],
            "total_projects_analyzed": len(agent.knowledge_base.projects),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error calculating project relevance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
