# test_db.py
import os
from app.core.database import engine, Base, SessionLocal
from app.models.schemas import Job
from datetime import datetime
import uuid

print("Testing database creation...")
print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./data/pipeline.db')}")

# Create tables
Base.metadata.create_all(bind=engine)
print("Tables created")

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")

# Try to insert a record
try:
    db = SessionLocal()
    test_job = Job(
        job_id=str(uuid.uuid4()),
        status="TEST",
        source_url="test_url",
        created_at=datetime.utcnow()
    )
    db.add(test_job)
    db.commit()
    print("Successfully inserted test record")
    
    # Query it back
    jobs = db.query(Job).all()
    print(f"Found {len(jobs)} jobs in database")
    db.close()
except Exception as e:
    print(f"Error: {e}")

print("Test complete")