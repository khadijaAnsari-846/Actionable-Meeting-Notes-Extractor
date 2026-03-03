# app/models/schemas.py
from sqlalchemy import Column, String, DateTime, Float, Text
from app.core.database import Base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# SQLAlchemy Model for the database
class Job(Base):
    __tablename__ = "jobs"
    
    job_id = Column(String, primary_key=True, index=True)
    status = Column(String, default="QUEUED")
    source_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    result = Column(Text, nullable=True)
    # Add these new fields for transcript
    transcript = Column(Text, nullable=True)
    transcript_preview = Column(String, nullable=True)

# Pydantic models for API responses
class JobResponse(BaseModel):
    """Response model for job status endpoint"""
    job_id: str
    status: str
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime
    result: Optional[Dict[str, Any]] = None
    transcript_preview: Optional[str] = None
    full_transcript_available: bool = False
    
    class Config:
        from_attributes = True

class TranscriptResponse(BaseModel):
    """Response model for full transcript endpoint"""
    job_id: str
    full_transcript: str
    word_count: int
    preview: str

class SalesCallInsights(BaseModel):
    """Insights extracted from sales calls"""
    summary: str = Field(description="A concise summary of the call.")
    competitors: List[str] = Field(description="Competitors mentioned by name.")
    budget: Optional[str] = Field(description="Mentioned budget or price sensitivity.")
    timeline: Optional[str] = Field(description="Decision timeline mentioned.")
    sentiment_score: float = Field(description="Overall sentiment from -1.0 to 1.0.")
    next_steps: List[str] = Field(description="Action items for the sales rep.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Customer discussed pricing concerns",
                "competitors": ["Competitor A", "Competitor B"],
                "budget": "$10,000-15,000",
                "timeline": "Next quarter",
                "sentiment_score": 0.7,
                "next_steps": ["Send pricing proposal", "Schedule follow-up call"]
            }
        }
        
        
# Add these at the VERY END of your schemas.py file
# Make sure there are no syntax errors or indentation issues

class TaskItem(BaseModel):
    task: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    priority: str = "Medium"

class SemanticAnalysis(BaseModel):
    overall_sentiment: float
    sentiment_trend: str
    communication_style: str
    tension_points: List[str] = []
    agreement_levels: Dict[str, str] = {}
    speaker_engagement: str

class MeetingInsights(BaseModel):
    cleaned_transcript: str
    tasks: List[TaskItem]
    key_decisions: List[str]
    important_points: List[str]
    summary: str
    semantic_analysis: SemanticAnalysis
    qa_context: Dict[str, Any]