# app/core/init_db.py
from app.core.database import engine, Base
import os
from pathlib import Path

def init_database():
    """Initialize the database and create all tables"""
    print("="*50)
    print("Creating database tables...")
    print(f"Current directory: {os.getcwd()}")
    
    # Ensure data directory exists
    Path("data").mkdir(parents=True, exist_ok=True)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables created: {tables}")
    print("Database initialization complete!")
    print("="*50)
    
    return tables

# If run directly
if __name__ == "__main__":
    init_database()