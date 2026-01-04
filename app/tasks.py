from celery import Celery
from app.db import SessionLocal
from app.models import GenerationTask
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    'sfera',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True)
def generate_content_task(self, task_id: int, prompt: str, user_id: int):
    """
    Background task for generating content using OpenAI
    """
    db = SessionLocal()
    try:
        task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
        if not task:
            return {"error": "Task not found"}
        
        # Update task status to processing
        task.status = "processing"
        db.commit()
        
        # Here you would call OpenAI API
        # For now, just mark as completed
        task.status = "completed"
        task.result_url = f"https://example.com/result/{task_id}"
        db.commit()
        
        return {"task_id": task_id, "status": "completed"}
    except Exception as e:
        task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
        if task:
            task.status = "failed"
            task.error = str(e)
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def process_carousel(carousel_id: int):
    """
    Process carousel generation
    """
    db = SessionLocal()
    try:
        # Process carousel logic here
        return {"carousel_id": carousel_id, "status": "processed"}
    finally:
        db.close()
