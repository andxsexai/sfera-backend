from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db import get_db
from app.models import User, Carousel, CreditTransaction, GenerationTask
import openai
import os

router = APIRouter(prefix="/api/v1", tags=["api"])

class GenerateRequest(BaseModel):
    prompt: str
    user_id: int

class GenerateResponse(BaseModel):
    task_id: int
    status: str
    message: str

@router.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequest, db: Session = Depends(get_db)):
    """Генерирует контент на основе prompt через OpenAI"""
    try:
        # Создаём задачу в БД
        task = GenerationTask(
            user_id=request.user_id,
            prompt=request.prompt,
            status="processing"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return GenerateResponse(
            task_id=task.id,
            status="processing",
            message="Content generation started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/carousels")
def get_carousels(db: Session = Depends(get_db)):
    """Получает все карусели"""
    carousels = db.query(Carousel).all()
    return {"carousels": carousels}

@router.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получает информацию о пользователе"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SFERA Backend API"}
