from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from database import get_db
import models, schemas, auth
from utils import cloudinary_helper

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/", response_model=List[schemas.CompanyResponse])
def list_companies(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Company)
    if search:
        query = query.filter(
            or_(
                models.Company.name.ilike(f"%{search}%"),
                models.Company.industry.ilike(f"%{search}%"),
                models.Company.description.ilike(f"%{search}%")
            )
        )
    return query.all()

@router.post("/", response_model=schemas.CompanyResponse)
def create_company(company_in: schemas.CompanyCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Placed students & admins can create companies to register new ones when sharing experiences
    if current_user.role not in ["admin", "placed student"]:
        raise HTTPException(status_code=403, detail="Only placed students or admins can create companies")
        
    existing = db.query(models.Company).filter(models.Company.name.ilike(company_in.name)).first()
    if existing:
        return existing
        
    db_company = models.Company(**company_in.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/{company_id}", response_model=schemas.CompanyResponse)
def get_company_details(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.post("/{company_id}/logo")
def upload_company_logo(company_id: int, file: UploadFile = File(...), current_user: models.User = Depends(auth.require_role(["admin", "placed student"])), db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    logo_url = cloudinary_helper.upload_image_or_file(file, folder="companies")
    company.logo_url = logo_url
    db.commit()
    return {"logo_url": logo_url, "message": "Company logo uploaded successfully"}

@router.get("/{company_id}/experiences", response_model=List[schemas.PlacementExperienceResponse])
def get_company_experiences(company_id: int, db: Session = Depends(get_db)):
    # Return approved experiences for the company
    return db.query(models.PlacementExperience).filter(
        models.PlacementExperience.company_id == company_id,
        models.PlacementExperience.is_approved == True
    ).order_by(models.PlacementExperience.created_at.desc()).all()

@router.get("/{company_id}/questions", response_model=List[schemas.InterviewQuestionResponse])
def get_company_questions(company_id: int, db: Session = Depends(get_db)):
    return db.query(models.InterviewQuestion).filter(
        models.InterviewQuestion.company_id == company_id
    ).order_by(models.InterviewQuestion.created_at.desc()).all()
