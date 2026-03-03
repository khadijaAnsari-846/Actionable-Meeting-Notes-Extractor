# app/services/processor.py
from crewai import Agent, Task, Crew, Process, LLM
import json
from app.models.schemas import MeetingInsights, TaskItem, SemanticAnalysis
from typing import List, Dict, Any, Optional
import os





#At the top of app/services/processor.py, replace the imports with:

# First, try to import all needed models
try:
    from app.models.schemas import MeetingInsights, TaskItem, SemanticAnalysis, SalesCallInsights
    print("✅ All schema imports successful")
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    # Fallback imports
    from app.models.schemas import MeetingInsights, TaskItem, SemanticAnalysis
    from app.models.schemas import SalesCallInsights  # Try separate import
   
   
   
    


hf_llm = LLM(
    model="huggingface/Qwen/Qwen2.5-Coder-7B-Instruct", 
    api_key=MY_HF_TOKEN,
    base_url="https://router.huggingface.co", 
    max_tokens=1024,
    temperature=0.1,
)

# ==================== AGENT 1: Transcript Auditor ====================
auditor = Agent(
    role='Transcript Auditor',
    goal='Clean the transcript and ensure technical terms are accurate',
    backstory='''You are a meticulous auditor who removes filler words (um, uh, like, you know), 
    corrects misspellings of company names, technical jargon, and ensures the transcript 
    is clean and readable for further analysis.''',
    verbose=True,
    max_iter=5,
    llm=hf_llm,
    allow_delegation=False
)

# ==================== AGENT 2: Task & Action Item Extractor ====================
task_extractor = Agent(
    role='Task & Action Item Extractor',
    goal='Extract all tasks, action items, and important points from the meeting',
    backstory='''You are a project manager specialized in extracting actionable items from meetings.
    You identify who is responsible for what, deadlines mentioned, and key decisions made.
    You create a structured list of tasks with owners and timelines.
    You distinguish between:
    - Explicit tasks ("John will send the report by Friday")
    - Implicit action items ("We need to follow up on that")
    - Key decisions ("We agreed to use AWS instead of Azure")
    - Important discussion points ("Budget constraints were discussed")''',
    verbose=True,
    llm=hf_llm,
    max_iter=5,
    allow_delegation=False
)

# ==================== AGENT 3: Meeting Summarizer ====================
summarizer = Agent(
    role='Meeting Summarizer',
    goal='Create concise, comprehensive meeting summaries',
    backstory='''You are an executive assistant who creates clear, actionable meeting summaries.
    You highlight key discussion points, decisions made, and provide a brief overview
    that anyone can read to understand what happened in the meeting in under 2 minutes.
    
    Your summaries include:
    - Executive summary (2-3 sentences)
    - Key discussion topics with brief context
    - All decisions made
    - Next steps and action items
    - Any blockers or risks identified''',
    verbose=True,
    llm=hf_llm,
    max_iter=5,
    allow_delegation=False
)

# ==================== AGENT 4: Semantic & Sentiment Analyst ====================
semantic_analyst = Agent(
    role='Semantic & Sentiment Analyst',
    goal='Analyze the emotional tone, delivery style, and communication patterns',
    backstory='''You are a communication expert who analyzes how information was delivered.
    You detect sentiment shifts, tension points, agreement levels, and overall meeting mood.
    You assess whether the conversation was collaborative, confrontational, neutral, or enthusiastic.
    
    You provide:
    - Overall sentiment score (-1.0 to 1.0)
    - Sentiment trend (improving, declining, stable, volatile)
    - Communication style (collaborative, formal, casual, tense, enthusiastic)
    - Specific moments of tension or strong agreement
    - Speaker engagement analysis
    - Topic-wise agreement levels''',
    verbose=True,
    llm=hf_llm,
    max_iter=5,
    allow_delegation=False
)

# ==================== AGENT 5: Q&A Context Builder ====================
qa_context_builder = Agent(
    role='Q&A Context Builder',
    goal='Prepare meeting data for question-answering retrieval',
    backstory='''You are a knowledge management expert who structures meeting content
    into searchable chunks with metadata. You identify key topics, entities, and
    create context snippets that can be retrieved for answering questions.
    
    For each chunk (100-200 words), you provide:
    - The text content
    - Main topics covered
    - Key entities (people, companies, dates, amounts, technical terms)
    - Timestamp if available
    
    You also create an overall topic map and entity index for the meeting.''',
    verbose=True,
    llm=hf_llm,
    max_iter=5,
    allow_delegation=False
)

# ==================== AGENT 6: Sales Analyst (for backward compatibility) ====================
analyst = Agent(
    role='Sales Analyst',
    goal='Extract key BANT data (Budget, Authority, Need, Timeline) and competitors',
    backstory='''You are a seasoned sales analyst expert at identifying buying signals, 
    pain points, and sales opportunities from conversation logs. You focus on:
    - Budget indicators and price sensitivity
    - Decision-maker authority levels
    - Customer needs and pain points
    - Decision timelines
    - Competitor mentions and positioning''',
    verbose=True,
    llm=hf_llm,
    max_iter=5,
    allow_delegation=False
)

# ==================== AGENT 7: CRM Formatter (for backward compatibility) ====================
formatter = Agent(
    role='CRM Formatter',
    goal='Format the analyzed data into a JSON structure for CRM upload',
    backstory='''You are a data engineer specialized in CRM data mapping who ensures
    all insights are properly structured for integration with sales systems.''',
    verbose=True,
    llm=hf_llm,
    allow_delegation=False,
    max_iter=5
)





# ==================== COMPREHENSIVE MEETING ANALYSIS ====================

def analyze_transcript(transcript_text: str) -> MeetingInsights:
    """
    Comprehensive meeting analysis returning:
    - Clean transcript
    - Task list with owners and deadlines
    - Key decisions and important points
    - Meeting summary
    - Semantic and sentiment analysis
    - Q&A context chunks
    """
    print("🚀 Starting comprehensive meeting analysis...")
    
    # Task 1: Clean the transcript
    audit_task = Task(
        description=f"""
        Clean and normalize this meeting transcript. Remove filler words (um, uh, like, you know),
        correct misspellings, fix grammar, and make it readable.
        
        TRANSCRIPT:
        {transcript_text}
        
        Return ONLY the cleaned transcript without any additional text or explanations.
        """,
        agent=auditor,
        expected_output="A cleaned, readable version of the transcript with filler words removed and grammar corrected."
    )
    
    # Task 2: Extract tasks and important points
    task_extraction_task = Task(
        description="""
        Analyze the transcript and extract:
        
        1. ACTION ITEMS/TASKS: For each task, identify:
           - Task description
           - Who is responsible (owner)
           - Deadline or timeline mentioned
           - Priority (High/Medium/Low based on urgency)
        
        2. KEY DECISIONS: What were the main decisions made?
        
        3. IMPORTANT POINTS: Key discussion points, concerns raised, insights shared
        
        Format your response as a valid JSON object with this exact structure:
        {
            "tasks": [
                {
                    "task": "Send the Q3 report",
                    "owner": "John",
                    "deadline": "Friday",
                    "priority": "High"
                }
            ],
            "key_decisions": ["We will use AWS for hosting", "Budget approved for Q3"],
            "important_points": ["Customer concerned about pricing", "Competitor mentioned"]
        }
        """,
        agent=task_extractor,
        expected_output="A JSON object containing tasks, key decisions, and important points."
    )
    
    # Task 3: Create meeting summary
    summary_task = Task(
        description="""
        Create a comprehensive meeting summary with these sections:
        
        EXECUTIVE SUMMARY: 2-3 sentences capturing the essence of the meeting
        
        KEY TOPICS DISCUSSED: Bullet points of main discussion areas with brief context
        
        DECISIONS MADE: List of all decisions agreed upon
        
        NEXT STEPS: Action items and follow-ups
        
        BLOCKERS/RISKS: Any issues or concerns raised
        
        Keep it concise but complete. Use clear section headers.
        """,
        agent=summarizer,
        expected_output="""A well-structured meeting summary with sections:
        EXECUTIVE SUMMARY
        KEY TOPICS DISCUSSED
        DECISIONS MADE
        NEXT STEPS
        BLOCKERS/RISKS"""
    )
    
    # Task 4: Analyze semantics and sentiment
    semantic_task = Task(
        description="""
        Analyze the emotional tone and communication patterns in this meeting.
        
        Provide:
        1. overall_sentiment: A float from -1.0 (very negative) to 1.0 (very positive)
        2. sentiment_trend: "improving", "declining", "stable", or "volatile"
        3. communication_style: One of ["collaborative", "formal", "casual", "tense", "enthusiastic", "neutral"]
        4. tension_points: List of specific moments where tension or disagreement occurred
        5. agreement_levels: Dictionary mapping topics to agreement levels ("high", "medium", "low")
        6. speaker_engagement: Description of how engaged participants seemed
        
        Format your response as a valid JSON object with this exact structure:
        {
            "overall_sentiment": 0.7,
            "sentiment_trend": "improving",
            "communication_style": "collaborative",
            "tension_points": ["When discussing budget constraints", "During timeline discussion"],
            "agreement_levels": {"budget": "medium", "timeline": "high"},
            "speaker_engagement": "All participants were actively engaged throughout"
        }
        """,
        agent=semantic_analyst,
        expected_output="A JSON object containing semantic and sentiment analysis."
    )
    
    # Task 5: Prepare Q&A context
    qa_context_task = Task(
        description="""
        Break down the meeting content into searchable chunks for Q&A.
        
        Create 3-7 chunks of 100-200 words each. For each chunk provide:
        - The text content
        - Main topics covered
        - Key entities mentioned (people, companies, dates, amounts)
        
        Also provide an overall topic list and entity index.
        
        Format your response as a valid JSON object with this exact structure:
        {
            "chunks": [
                {
                    "text": "The discussion about budget allocation...",
                    "topics": ["budget", "planning"],
                    "entities": ["Q3", "$50,000", "Marketing team"]
                }
            ],
            "key_topics": ["budget", "timeline", "competitors"],
            "entities": {
                "people": ["John", "Sarah"],
                "companies": ["Competitor A", "AWS"],
                "dates": ["Friday", "next week"],
                "amounts": ["$50,000"]
            }
        }
        """,
        agent=qa_context_builder,
        expected_output="A JSON object with chunks, key topics, and entities for Q&A retrieval."
    )
    
    # Task 6: Validate and finalize insights
    # Create the Crew with sequential processing
    crew = Crew(
        agents=[auditor, task_extractor, summarizer, semantic_analyst, qa_context_builder],
        tasks=[audit_task, task_extraction_task, summary_task, semantic_task, qa_context_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the crew
    result = crew.kickoff()
    
    # Parse the results
    try:
        # Extract outputs from each task
        cleaned_transcript = result.tasks_output[0].raw if hasattr(result, 'tasks_output') else str(result)
        
        # Parse JSON outputs
        tasks_data = json.loads(result.tasks_output[1].raw) if hasattr(result, 'tasks_output') else {}
        semantic_data = json.loads(result.tasks_output[3].raw) if hasattr(result, 'tasks_output') else {}
        qa_data = json.loads(result.tasks_output[4].raw) if hasattr(result, 'tasks_output') else {}
        
        # Create TaskItem objects
        tasks = []
        for task_item in tasks_data.get('tasks', []):
            tasks.append(TaskItem(
                task=task_item.get('task', ''),
                owner=task_item.get('owner'),
                deadline=task_item.get('deadline'),
                priority=task_item.get('priority', 'Medium')
            ))
        
        # Create SemanticAnalysis object
        semantic_analysis = SemanticAnalysis(
            overall_sentiment=semantic_data.get('overall_sentiment', 0.0),
            sentiment_trend=semantic_data.get('sentiment_trend', 'stable'),
            communication_style=semantic_data.get('communication_style', 'neutral'),
            tension_points=semantic_data.get('tension_points', []),
            agreement_levels=semantic_data.get('agreement_levels', {}),
            speaker_engagement=semantic_data.get('speaker_engagement', '')
        )
        
        # Create MeetingInsights object
        meeting_insights = MeetingInsights(
            cleaned_transcript=cleaned_transcript,
            tasks=tasks,
            key_decisions=tasks_data.get('key_decisions', []),
            important_points=tasks_data.get('important_points', []),
            summary=result.tasks_output[2].raw if hasattr(result, 'tasks_output') else '',
            semantic_analysis=semantic_analysis,
            qa_context=qa_data
        )
        
        print("✅ Comprehensive analysis complete!")
        return meeting_insights
        
    except Exception as e:
        print(f"❌ Error parsing analysis results: {e}")
        import traceback
        traceback.print_exc()
        
        # Return basic insights if parsing fails
        return MeetingInsights(
            cleaned_transcript=transcript_text,
            tasks=[],
            key_decisions=[],
            important_points=[],
            summary="Analysis failed to parse properly",
            semantic_analysis=SemanticAnalysis(
                overall_sentiment=0.0,
                sentiment_trend="unknown",
                communication_style="unknown",
                tension_points=[],
                agreement_levels={},
                speaker_engagement="Analysis failed"
            ),
            qa_context={}
        )

# ==================== BACKWARD COMPATIBILITY ====================

def analyze_transcript_simple(transcript_text: str) -> SalesCallInsights:
    """
    Original simple analysis function for sales calls (backward compatibility)
    """
    print("🔍 Running simple sales analysis...")
    
    # Task 1: Audit
    audit_task = Task(
        description=f"Clean this sales call transcript: {transcript_text[:1000]}...",
        agent=auditor,
        expected_output="A cleaned version of the transcript."
    )
    
    # Task 2: Analyze
    analyze_task = Task(
        description="""
        Extract the following from the cleaned transcript:
        - Summary of the call
        - Competitors mentioned
        - Budget or price sensitivity mentioned
        - Decision timeline
        - Overall sentiment (-1.0 to 1.0)
        - Next steps or action items
        """,
        agent=analyst,
        expected_output="Structured insights about the sales call."
    )
    
    # Task 3: Format
    format_task = Task(
        description="Format the analysis into the required JSON structure matching SalesCallInsights schema.",
        agent=formatter,
        expected_output="JSON data matching the SalesCallInsights schema.",
        output_json=SalesCallInsights
    )
    
    crew = Crew(
        agents=[auditor, analyst, formatter],
        tasks=[audit_task, analyze_task, format_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return result

# ==================== HELPER FUNCTIONS FOR CHATBOT ====================

def format_tasks_for_display(meeting_insights: MeetingInsights) -> str:
    """Format tasks into a readable list"""
    if not meeting_insights.tasks:
        return "No tasks identified in this meeting."
    
    output = "📋 **TASKS & ACTION ITEMS**\n\n"
    for i, task in enumerate(meeting_insights.tasks, 1):
        output += f"{i}. **{task.task}**\n"
        if task.owner:
            output += f"   - Owner: {task.owner}\n"
        if task.deadline:
            output += f"   - Deadline: {task.deadline}\n"
        output += f"   - Priority: {task.priority}\n\n"
    
    return output

def format_key_decisions(meeting_insights: MeetingInsights) -> str:
    """Format key decisions into a readable list"""
    if not meeting_insights.key_decisions:
        return "No key decisions recorded."
    
    output = "✅ **KEY DECISIONS**\n\n"
    for decision in meeting_insights.key_decisions:
        output += f"• {decision}\n"
    
    return output

def format_semantic_analysis(meeting_insights: MeetingInsights) -> str:
    """Format semantic analysis into readable text"""
    sa = meeting_insights.semantic_analysis
    
    sentiment_emoji = "😊" if sa.overall_sentiment > 0.3 else "😐" if sa.overall_sentiment > -0.3 else "😞"
    
    output = f"📊 **SEMANTIC ANALYSIS**\n\n"
    output += f"{sentiment_emoji} **Overall Sentiment:** {sa.overall_sentiment:.2f}\n"
    output += f"📈 **Sentiment Trend:** {sa.sentiment_trend}\n"
    output += f"💬 **Communication Style:** {sa.communication_style}\n\n"
    
    if sa.tension_points:
        output += "⚠️ **Tension Points:**\n"
        for point in sa.tension_points:
            output += f"   • {point}\n"
        output += "\n"
    
    if sa.agreement_levels:
        output += "🤝 **Agreement by Topic:**\n"
        for topic, level in sa.agreement_levels.items():
            output += f"   • {topic}: {level}\n"
    
    return output

# For direct testing
if __name__ == "__main__":
    # Test with a sample transcript
    sample = "This is a test meeting transcript about budget planning..."
    result = analyze_transcript(sample)
    print(format_tasks_for_display(result))