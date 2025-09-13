from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.nl_to_sql import nl_to_sql_service

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a natural language query and return property search results
    """
    try:
        result = await nl_to_sql_service.process_query(request.message, db)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{query_id}")
async def submit_feedback(query_id: str, score: int, db: Session = Depends(get_db)):
    """
    Submit feedback for a query to improve the AI system
    """
    if score < 1 or score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")
    
    try:
        nl_to_sql_service.submit_feedback(db, query_id, score)
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))