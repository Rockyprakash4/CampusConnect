from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/questions", tags=["Interview Questions"])

@router.get("/", response_model=List[schemas.InterviewQuestionResponse])
def list_questions(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    company_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.InterviewQuestion)
    
    if category:
        query = query.filter(models.InterviewQuestion.category == category)
        
    if difficulty:
        query = query.filter(models.InterviewQuestion.difficulty == difficulty)
        
    if company_id:
        query = query.filter(models.InterviewQuestion.company_id == company_id)
        
    if search:
        query = query.join(models.Company).filter(
            or_(
                models.Company.name.ilike(f"%{search}%"),
                models.InterviewQuestion.role.ilike(f"%{search}%"),
                models.InterviewQuestion.question_text.ilike(f"%{search}%"),
                models.InterviewQuestion.topic.ilike(f"%{search}%")
            )
        )
        
    return query.order_by(models.InterviewQuestion.created_at.desc()).all()

@router.post("/", response_model=schemas.InterviewQuestionResponse)
def create_question(req: schemas.InterviewQuestionCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Check or create company
    company_name_clean = req.company_name.strip()
    company = db.query(models.Company).filter(models.Company.name.ilike(company_name_clean)).first()
    
    if not company:
        company = models.Company(
            name=company_name_clean,
            website=f"https://www.google.com/search?q={company_name_clean}",
            industry="Technology"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
    db_question = models.InterviewQuestion(
        user_id=current_user.id,
        company_id=company.id,
        role=req.role,
        category=req.category,
        question_text=req.question_text,
        answer_text=req.answer_text,
        difficulty=req.difficulty,
        topic=req.topic
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.delete("/{question_id}")
def delete_question(question_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    question = db.query(models.InterviewQuestion).filter(models.InterviewQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    if current_user.role != "admin" and question.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this question")
        
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}
