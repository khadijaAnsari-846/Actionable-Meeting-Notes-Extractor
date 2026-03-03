# app/routers/chat.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import Job
import json
from typing import Optional, List
from app.services.processor import format_tasks_for_display, format_key_decisions, format_semantic_analysis

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    job_id: str
    question: str

class ChatResponse(BaseModel):
    job_id: str
    question: str
    answer: str
    relevant_sections: Optional[List[str]] = None

@router.post("/ask", response_model=ChatResponse)
async def ask_about_meeting(request: ChatRequest, db: Session = Depends(get_db)):
    """Ask questions about a specific meeting"""
    job = db.query(Job).filter(Job.job_id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.result:
        raise HTTPException(status_code=404, detail="Meeting analysis not available yet")
    
    try:
        # Parse the stored insights
        insights = json.loads(job.result)
        
        # For now, use a simple keyword matching approach
        # Later you can implement proper RAG with embeddings
        question_lower = request.question.lower()
        answer = "I couldn't find specific information about that in the meeting notes."
        
        # Check for task-related questions
        if any(word in question_lower for word in ["task", "action", "to-do", "assign"]):
            if "tasks" in insights:
                tasks_text = format_tasks_for_display_from_dict(insights)
                answer = f"Here are the tasks from the meeting:\n\n{tasks_text}"
        
        # Check for decision-related questions
        elif any(word in question_lower for word in ["decision", "decide", "agreed"]):
            if "key_decisions" in insights and insights["key_decisions"]:
                decisions = "\n".join([f"• {d}" for d in insights["key_decisions"]])
                answer = f"Key decisions made in the meeting:\n\n{decisions}"
            else:
                answer = "No key decisions were recorded in this meeting."
        
        # Check for sentiment questions
        elif any(word in question_lower for word in ["sentiment", "tone", "mood", "feeling"]):
            if "semantic_analysis" in insights:
                sa = insights["semantic_analysis"]
                sentiment_emoji = "😊" if sa.get("overall_sentiment", 0) > 0.3 else "😐" if sa.get("overall_sentiment", 0) > -0.3 else "😞"
                answer = f"{sentiment_emoji} Overall sentiment: {sa.get('overall_sentiment', 0)}\n"
                answer += f"📈 Trend: {sa.get('sentiment_trend', 'stable')}\n"
                answer += f"💬 Style: {sa.get('communication_style', 'neutral')}"
        
        # Check for summary questions
        elif any(word in question_lower for word in ["summary", "summarize", "overview", "about"]):
            if "summary" in insights:
                answer = f"Meeting Summary:\n\n{insights['summary']}"
        
        return ChatResponse(
            job_id=request.job_id,
            question=request.question,
            answer=answer
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

def format_tasks_for_display_from_dict(insights: dict) -> str:
    """Helper to format tasks from dictionary"""
    tasks = insights.get("tasks", [])
    if not tasks:
        return "No tasks identified."
    
    output = ""
    for i, task in enumerate(tasks, 1):
        output += f"{i}. **{task.get('task')}**\n"
        if task.get('owner'):
            output += f"   - Owner: {task['owner']}\n"
        if task.get('deadline'):
            output += f"   - Deadline: {task['deadline']}\n"
        output += f"   - Priority: {task.get('priority', 'Medium')}\n\n"
    
    return output