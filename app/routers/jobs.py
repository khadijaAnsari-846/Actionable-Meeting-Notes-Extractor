# app/routers/jobs.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import Job, JobResponse, TranscriptResponse
from typing import Optional
import json

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Parse result JSON if it exists
    result_data = None
    if job.result:
        try:
            result_data = json.loads(job.result)
        except:
            result_data = {"raw": job.result}
    
    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        source_url=job.source_url,
        file_path=job.file_path,
        created_at=job.created_at,
        result=result_data,
        transcript_preview=job.transcript_preview,
        full_transcript_available=job.transcript is not None
    )

@router.get("/{job_id}/transcript", response_model=TranscriptResponse)
def get_full_transcript(
    job_id: str, 
    words: Optional[int] = Query(None, description="Number of words to return (optional)"),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.transcript:
        raise HTTPException(status_code=404, detail="Transcript not available yet")
    
    full_transcript = job.transcript
    word_count = len(full_transcript.split())
    
    # If words parameter is provided, return only that many words
    if words:
        transcript_words = full_transcript.split()[:words]
        display_transcript = " ".join(transcript_words)
        if words < word_count:
            display_transcript += "..."
    else:
        display_transcript = full_transcript
    
    # Create a preview (first 20 words for the preview field)
    preview_words = full_transcript.split()[:20]
    preview = " ".join(preview_words) + "..." if word_count > 20 else full_transcript
    
    return TranscriptResponse(
        job_id=job.job_id,
        full_transcript=display_transcript,
        word_count=min(words, word_count) if words else word_count,
        preview=preview
    )

# Optional: Add endpoint to get just the preview
@router.get("/{job_id}/preview")
def get_transcript_preview(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.job_id,
        "preview": job.transcript_preview or "No preview available",
        "status": job.status
    }