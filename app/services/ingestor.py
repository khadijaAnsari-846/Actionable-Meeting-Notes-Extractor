# app/services/ingestor.py
import yt_dlp
import os
import shutil
import json
from pathlib import Path
from app.core.database import SessionLocal
from app.models.schemas import Job
from app.services.transcriber import TranscriberService
from app.services.processor import analyze_transcript

DATA_DIR = Path("data/uploads")
DATA_DIR.mkdir(parents=True, exist_ok=True)

class IngestorService:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.folder = DATA_DIR / job_id
        self.folder.mkdir(exist_ok=True)

    def _update_db_status(self, job_id, status, transcript=None, preview=None):
        """Update job status in database"""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = status
                if transcript is not None:
                    job.transcript = transcript
                if preview is not None:
                    job.transcript_preview = preview
                db.commit()
                print(f"✅ Job {job_id} status updated to: {status}")
        except Exception as e:
            print(f"❌ Error updating job status: {e}")
            db.rollback()
        finally:
            db.close()

    async def save_file(self, upload_file):
        """Save uploaded file to disk"""
        file_path = self.folder / upload_file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        print(f"✅ File saved: {file_path}")
        return str(file_path)

    def handle_url(self, url: str):
        """Handle URL download (YouTube, etc.)"""
        self._update_db_status(self.job_id, "DOWNLOADING")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.folder}/audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            print(f"⬇️ Downloading from URL: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            audio_path = self.folder / "audio.mp3"
            print(f"✅ Download complete: {audio_path}")
            # Hand off to the pipeline once download is done
            self.trigger_pipeline(str(audio_path))
        except Exception as e:
            error_msg = f"FAILED DOWNLOAD: {str(e)}"
            print(f"❌ {error_msg}")
            self._update_db_status(self.job_id, error_msg)

    def trigger_pipeline(self, file_path: str):
        """
        Main pipeline: Transcribe -> Analyze -> Store Results
        """
        print(f"🚀 Starting pipeline for job {self.job_id}")
        self._update_db_status(self.job_id, "TRANSCRIBING")
        
        try:
            # Step 1: Transcribe the audio
            print("🎤 Starting transcription...")
            transcriber = TranscriberService()
            
            # Get transcription results (returns 3 values)
            segments, full_text, preview = transcriber.transcribe_file(file_path)
            print(f"✅ Transcription complete: {len(full_text.split())} words")
            print(f"📝 Preview: {preview}")
            
            # Update database with transcript
            self._update_db_status(
                self.job_id, 
                "TRANSCRIBING",
                transcript=full_text,
                preview=preview
            )
            
            # Step 2: Update status to Analyzing
            print("🔍 Starting analysis...")
            self._update_db_status(self.job_id, "ANALYZING")
            
            # Step 3: Run Agentic Analysis
            insights = analyze_transcript(full_text)
            print("✅ Analysis complete")
            
            # Step 4: Update DB with final structured result
            db = SessionLocal()
            try:
                job = db.query(Job).filter(Job.job_id == self.job_id).first()
                if job:
                    # Convert insights to JSON
                    if hasattr(insights, 'model_dump_json'):
                        # Pydantic v2
                        result_json = insights.model_dump_json()
                    elif hasattr(insights, 'json'):
                        # Pydantic v1
                        result_json = insights.json()
                    else:
                        # Dictionary or other
                        result_json = json.dumps(insights)
                    
                    job.result = result_json
                    job.status = "COMPLETED"
                    db.commit()
                    print(f"✅ Results saved to database for job {self.job_id}")
            except Exception as e:
                print(f"❌ Error saving results: {e}")
                db.rollback()
            finally:   
                db.close()
            
            print(f"🎉 Pipeline completed successfully for {self.job_id}")
            
        except Exception as e:
            error_msg = f"FAILED PIPELINE: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self._update_db_status(self.job_id, error_msg)

    def get_job_details(self):
        """Helper method to get current job details"""
        db = SessionLocal()
        try:
            job = db.query(Job).filter(Job.job_id == self.job_id).first()
            if job:
                return {
                    "job_id": job.job_id,
                    "status": job.status,
                    "transcript_preview": job.transcript_preview,
                    "has_transcript": job.transcript is not None,
                    "has_result": job.result is not None
                }
            return None
        finally:
            db.close()