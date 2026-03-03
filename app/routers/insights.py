# app/routers/insights.py
print("="*60)
print("🔧 INSIGHTS.PY IS BEING LOADED")
print("="*60)

import sys
print(f"Python file: {__file__}")
print(f"Module name: {__name__}")

from fastapi import APIRouter, HTTPException, Depends
print("✅ FastAPI imports successful")

from sqlalchemy.orm import Session
print("✅ SQLAlchemy imports successful")

from app.core.database import get_db
print("✅ Database imports successful")

from app.models.schemas import Job, MeetingInsights, TaskItem, SemanticAnalysis
print("✅ Schema imports successful")

from typing import List, Dict, Any, Optional
import json
print("✅ Standard library imports successful")

# Create router
print("🔧 Creating router...")
router = APIRouter(prefix="/insights", tags=["Meeting Insights"])
print(f"✅ Router created: {router}")

# Define endpoints
@router.get("/{job_id}/summary")
def get_meeting_summary(job_id: str, db: Session = Depends(get_db)):
    """Get the meeting summary"""
    print(f"📝 Getting summary for job {job_id}")
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        return {
            "job_id": job_id,
            "summary": insights.get("summary", "No summary available")
        }
    except Exception as e:
        print(f"❌ Error parsing insights: {e}")
        raise HTTPException(status_code=500, detail="Error parsing insights")

@router.get("/{job_id}/tasks", response_model=List[Dict[str, Any]])
def get_meeting_tasks(job_id: str, db: Session = Depends(get_db)):
    """Get all tasks from the meeting"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        tasks = insights.get("tasks", [])
        return tasks
    except:
        raise HTTPException(status_code=500, detail="Error parsing insights")

@router.get("/{job_id}/decisions")
def get_key_decisions(job_id: str, db: Session = Depends(get_db)):
    """Get key decisions from the meeting"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        return {
            "job_id": job_id,
            "key_decisions": insights.get("key_decisions", [])
        }
    except:
        raise HTTPException(status_code=500, detail="Error parsing insights")

@router.get("/{job_id}/important-points")
def get_important_points(job_id: str, db: Session = Depends(get_db)):
    """Get important points from the meeting"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        return {
            "job_id": job_id,
            "important_points": insights.get("important_points", [])
        }
    except:
        raise HTTPException(status_code=500, detail="Error parsing insights")

@router.get("/{job_id}/sentiment")
def get_sentiment_analysis(job_id: str, db: Session = Depends(get_db)):
    """Get sentiment and semantic analysis"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        return {
            "job_id": job_id,
            "semantic_analysis": insights.get("semantic_analysis", {})
        }
    except:
        raise HTTPException(status_code=500, detail="Error parsing insights")

@router.get("/{job_id}/full-insights")
def get_full_insights(job_id: str, db: Session = Depends(get_db)):
    """Get all insights at once"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        return {
            "job_id": job_id,
            "summary": insights.get("summary", ""),
            "tasks": insights.get("tasks", []),
            "key_decisions": insights.get("key_decisions", []),
            "important_points": insights.get("important_points", []),
            "semantic_analysis": insights.get("semantic_analysis", {}),
            "qa_context": insights.get("qa_context", {})
        }
    except:
        raise HTTPException(status_code=500, detail="Error parsing insights")

@router.get("/{job_id}/qa-context")
def get_qa_context(job_id: str, db: Session = Depends(get_db)):
    """Get Q&A context chunks for semantic search"""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Analysis not available yet")
    
    try:
        insights = json.loads(job.result)
        return {
            "job_id": job_id,
            "qa_context": insights.get("qa_context", {})
        }
    except:
        raise HTTPException(status_code=500, detail="Error parsing insights")

print("✅ All endpoints registered")
print(f"📋 Router has {len(router.routes)} routes")
print("="*60)