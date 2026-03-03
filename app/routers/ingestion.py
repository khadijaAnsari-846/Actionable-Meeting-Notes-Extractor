# app/routers/ingestion.py
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from typing import Optional
import uuid
import os
from app.services.ingestor import IngestorService
from app.models.schemas import Job
from app.core.database import SessionLocal, get_db
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/upload")
async def upload_source(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    
    # Validation: Ensure we have at least one input
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide either a file or a URL.")

    try:
        # Create job record in database FIRST
        new_job = Job(
            job_id=job_id,
            status="QUEUED",
            source_url=url if url else None,
            file_path=None,
            created_at=datetime.utcnow(),
            result=None
        )
        db.add(new_job)
        db.commit()
        print(f"Job {job_id} created successfully in database")
    except Exception as e:
        print(f"Error creating job in database: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Ingestor logic handles the heavy lifting
    ingestor = IngestorService(job_id)
    
    if file:
        file_path = await ingestor.save_file(file)
        # Trigger Background Job (Whisper)
        background_tasks.add_task(ingestor.trigger_pipeline, file_path)
        return {"job_id": job_id, "status": "processing", "source": "file"}

    if url:
        # Trigger Background Job (Download + Whisper)
        background_tasks.add_task(ingestor.handle_url, url)
        return {"job_id": job_id, "status": "queued", "source": "url"}