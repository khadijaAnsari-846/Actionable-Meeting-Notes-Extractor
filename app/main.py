# app/main.py
from fastapi import FastAPI
from app.routers import ingestion, jobs, chat, insights  # Add insights router
from app.core.init_db import init_database
import uvicorn

# Initialize database
init_database()

app = FastAPI(title="CRM Intelligence Pipeline")

# Include Routers
app.include_router(ingestion.router)
app.include_router(jobs.router)
app.include_router(chat.router)
app.include_router(insights.router)  # Add this line

@app.get("/")
def root():
    return {"message": "CRM Intelligence Pipeline API is running"}

@app.on_event("startup")
async def startup_event():
    print("Application startup complete")
    # Verify database on startup
    from app.core.database import SessionLocal
    from sqlalchemy import inspect
    db = SessionLocal()
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    print(f"Database tables at startup: {tables}")
    db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)