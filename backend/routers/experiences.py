from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from typing import List, Optional
import io

from database import get_db
import models, schemas, auth
from utils import cloudinary_helper, pdf_generator

router = APIRouter(prefix="/experiences", tags=["Placement Experiences"])

@router.get("/analytics/public")
def get_public_analytics(db: Session = Depends(get_db)):
    """
    Exposes placement statistics, average CTCs, and department wise metrics for Chart.js.
    """
    total_students = db.query(models.User).filter(models.User.role != "admin").count()
    placed_students = db.query(models.User).filter(models.User.placement_status == "placed").count()
    total_companies = db.query(models.Company).count()
    total_experiences = db.query(models.PlacementExperience).filter(models.PlacementExperience.is_approved == True).count()
    
    placement_ratio = (placed_students / total_students * 100) if total_students > 0 else 0
    
    # Top Hiring Companies (Selected Students)
    top_hiring = db.query(
        models.Company.name,
        func.count(models.PlacementExperience.id).label("hires_count")
    ).join(models.PlacementExperience).filter(
        models.PlacementExperience.is_approved == True,
        models.PlacementExperience.result == "Selected"
    ).group_by(models.Company.name).order_by(desc("hires_count")).limit(5).all()
    
    top_hiring_list = [{"company": r[0], "count": r[1]} for r in top_hiring]
    
    # Department Wise Placements
    dept_placements = db.query(
        models.User.department,
        func.count(models.User.id).label("count")
    ).filter(
        models.User.placement_status == "placed",
        models.User.department != None
    ).group_by(models.User.department).all()
    
    dept_list = [{"department": r[0], "count": r[1]} for r in dept_placements]
    
    # Packages Overview (Average vs Highest per company)
    packages_overview = db.query(
        models.Company.name,
        models.Company.average_package,
        models.Company.highest_package
    ).filter(models.Company.average_package != None).order_by(desc(models.Company.highest_package)).limit(5).all()
    
    packages_list = [{"company": r[0], "average": r[1], "highest": r[2]} for r in packages_overview]
    
    return {
        "stats": {
            "total_students": total_students,
            "placed_students": placed_students,
            "total_companies": total_companies,
            "total_experiences": total_experiences,
            "placement_ratio": round(placement_ratio, 2)
        },
        "top_hiring": top_hiring_list,
        "department_placements": dept_list,
        "packages_overview": packages_list
    }


@router.get("/", response_model=List[schemas.PlacementExperienceResponse])
def list_experiences(
    search: Optional[str] = None,
    company_id: Optional[int] = None,
    role: Optional[str] = None,
    min_ctc: Optional[float] = None,
    difficulty: Optional[str] = None,
    result: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.PlacementExperience).filter(models.PlacementExperience.is_approved == True)
    
    if company_id:
        query = query.filter(models.PlacementExperience.company_id == company_id)
        
    if role:
        query = query.filter(models.PlacementExperience.job_role.ilike(f"%{role}%"))
        
    if min_ctc:
        query = query.filter(models.PlacementExperience.ctc >= min_ctc)
        
    if difficulty:
        query = query.filter(models.PlacementExperience.difficulty == difficulty)
        
    if result:
        query = query.filter(models.PlacementExperience.result == result)
        
    if tag:
        query = query.filter(models.PlacementExperience.tags.ilike(f"%{tag}%"))
        
    if search:
        query = query.join(models.Company).filter(
            or_(
                models.Company.name.ilike(f"%{search}%"),
                models.PlacementExperience.job_role.ilike(f"%{search}%"),
                models.PlacementExperience.experience_details.ilike(f"%{search}%"),
                models.PlacementExperience.tags.ilike(f"%{search}%")
            )
        )
        
    return query.order_by(models.PlacementExperience.created_at.desc()).all()

@router.post("/", response_model=schemas.PlacementExperienceResponse)
def create_experience(exp_in: schemas.PlacementExperienceCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["placed student", "admin"]:
        raise HTTPException(status_code=403, detail="Only placed students or admins can share placement experiences")
        
    # Check or create company
    company_name_clean = exp_in.company_name.strip()
    company = db.query(models.Company).filter(models.Company.name.ilike(company_name_clean)).first()
    
    if not company:
        company = models.Company(
            name=company_name_clean,
            website=f"https://www.google.com/search?q={company_name_clean}",
            industry="Technology",
            average_package=exp_in.ctc,
            highest_package=exp_in.ctc
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    else:
        # Recalculate packages
        if company.average_package:
            company.average_package = round((company.average_package + exp_in.ctc) / 2, 2)
        else:
            company.average_package = exp_in.ctc
        if not company.highest_package or exp_in.ctc > company.highest_package:
            company.highest_package = exp_in.ctc
        db.commit()
        
    # Build experience record
    data = exp_in.model_dump(exclude={"company_name"})
    db_exp = models.PlacementExperience(
        **data,
        user_id=current_user.id,
        company_id=company.id,
        is_approved=(current_user.role == "admin") # Admin posts auto-approve, students require moderation
    )
    
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    
    # Notify admin for approval if not pre-approved
    if not db_exp.is_approved:
        admins = db.query(models.User).filter(models.User.role == "admin").all()
        for admin in admins:
            db.add(models.Notification(
                user_id=admin.id,
                actor_id=current_user.id,
                type="admin_alert",
                parent_type="experience",
                parent_id=db_exp.id,
                message=f"Placement Experience for {company.name} shared by {current_user.username} is pending review."
            ))
        db.commit()
        
    return db_exp

@router.get("/{experience_id}", response_model=schemas.PlacementExperienceResponse)
def get_experience(experience_id: int, current_user: Optional[models.User] = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    experience = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Placement experience not found")
        
    # Unapproved can only be viewed by author or admin
    if not experience.is_approved:
        if not current_user:
            raise HTTPException(status_code=403, detail="You do not have access to this unapproved experience")
        user = auth.get_current_user(current_user, db)
        if user.role != "admin" and experience.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have access to this unapproved experience")
            
    return experience

@router.put("/{experience_id}", response_model=schemas.PlacementExperienceResponse)
def update_experience(experience_id: int, exp_in: schemas.PlacementExperienceCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    experience = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
        
    if current_user.role != "admin" and experience.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this experience")
        
    # Update fields
    for field, value in exp_in.model_dump(exclude={"company_name"}).items():
        setattr(experience, field, value)
        
    db.commit()
    db.refresh(experience)
    return experience

@router.delete("/{experience_id}")
def delete_experience(experience_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    experience = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
        
    if current_user.role != "admin" and experience.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this experience")
        
    db.delete(experience)
    db.commit()
    return {"message": "Placement experience deleted successfully"}

@router.post("/{experience_id}/attachment")
def upload_experience_attachment(experience_id: int, file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    experience = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == experience_id).first()
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
        
    if current_user.role != "admin" and experience.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this experience")
        
    url = cloudinary_helper.upload_image_or_file(file, folder="experiences")
    experience.attachment_url = url
    db.commit()
    return {"attachment_url": url, "message": "Attachment uploaded successfully"}

@router.get("/{experience_id}/pdf")
def download_experience_pdf(experience_id: int, db: Session = Depends(get_db)):
    experience = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == experience_id).first()
    if not experience or not experience.is_approved:
        raise HTTPException(status_code=404, detail="Approved placement experience not found")
        
    pdf_buffer = pdf_generator.generate_experience_pdf(experience)
    filename = f"{experience.company.name.replace(' ', '_')}_{experience.job_role.replace(' ', '_')}_experience.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
