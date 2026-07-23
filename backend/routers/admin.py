from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models, schemas, auth

router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"],
    dependencies=[Depends(auth.require_role(["admin"]))]
)

class RoleUpdateRequest(BaseModel):
    role: str

class ReportActionRequest(BaseModel):
    action: str # resolve, dismiss, delete_item

# -----------------------------------------------------
# User Management
# -----------------------------------------------------
@router.get("/users", response_model=List[schemas.UserResponse])
def admin_list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.put("/users/{user_id}/role")
def admin_update_user_role(user_id: int, req: RoleUpdateRequest, db: Session = Depends(get_db)):
    if req.role not in ["student", "placed student", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role value")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.role = req.role
    db.commit()
    return {"message": f"User role updated to {req.role}"}

@router.delete("/users/{user_id}")
def admin_delete_user(user_id: int, current_admin: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_admin.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# -----------------------------------------------------
# Content Approvals
# -----------------------------------------------------
@router.get("/experiences/pending", response_model=List[schemas.PlacementExperienceResponse])
def admin_list_pending_experiences(db: Session = Depends(get_db)):
    return db.query(models.PlacementExperience).filter(
        models.PlacementExperience.is_approved == False
    ).order_by(models.PlacementExperience.created_at.desc()).all()

@router.post("/experiences/{experience_id}/approve")
def admin_approve_experience(experience_id: int, db: Session = Depends(get_db)):
    exp = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == experience_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
        
    if exp.is_approved:
        return {"message": "Experience is already approved"}
        
    exp.is_approved = True
    
    # Notify contributor
    db.add(models.Notification(
        user_id=exp.user_id,
        actor_id=exp.user_id, # Self or system
        type="post_approval",
        parent_type="experience",
        parent_id=exp.id,
        message=f"Congratulations! Your placement experience for {exp.company.name} has been approved."
    ))
    
    # Check if there are other unapproved notifications and mark them read
    db.query(models.Notification).filter(
        models.Notification.parent_type == "experience",
        models.Notification.parent_id == exp.id,
        models.Notification.type == "admin_alert"
    ).update({"is_read": True}, synchronize_session=False)
    
    db.commit()
    return {"message": "Experience approved successfully"}


# -----------------------------------------------------
# Moderation & Reports
# -----------------------------------------------------
@router.get("/reports", response_model=List[schemas.ReportResponse])
def admin_list_reports(db: Session = Depends(get_db)):
    return db.query(models.Report).order_by(models.Report.created_at.desc()).all()

@router.post("/reports/{report_id}/action")
def admin_take_report_action(report_id: int, req: ReportActionRequest, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if req.action == "dismiss":
        report.status = "Dismissed"
        db.commit()
        return {"message": "Report dismissed"}
        
    elif req.action == "resolve":
        report.status = "Resolved"
        db.commit()
        return {"message": "Report marked as resolved"}
        
    elif req.action == "delete_item":
        # Delete underlying reported item
        if report.parent_type == "experience":
            item = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == report.parent_id).first()
        elif report.parent_type == "question":
            item = db.query(models.InterviewQuestion).filter(models.InterviewQuestion.id == report.parent_id).first()
        elif report.parent_type == "roadmap":
            item = db.query(models.Roadmap).filter(models.Roadmap.id == report.parent_id).first()
        elif report.parent_type == "comment":
            item = db.query(models.Comment).filter(models.Comment.id == report.parent_id).first()
        else:
            item = None
            
        if item:
            db.delete(item)
            
        report.status = "Resolved"
        db.commit()
        return {"message": "Item deleted and report resolved"}
        
    raise HTTPException(status_code=400, detail="Invalid action")


# -----------------------------------------------------
# Placement Analytics
# -----------------------------------------------------
@router.get("/analytics")
def admin_get_analytics(db: Session = Depends(get_db)):
    # 1. Total Stats
    total_students = db.query(models.User).filter(models.User.role != "admin").count()
    placed_students = db.query(models.User).filter(models.User.placement_status == "placed").count()
    total_companies = db.query(models.Company).count()
    total_experiences = db.query(models.PlacementExperience).filter(models.PlacementExperience.is_approved == True).count()
    
    placement_ratio = (placed_students / total_students * 100) if total_students > 0 else 0
    
    # 2. Company Hires count & details
    # Group experiences by company to see who hires the most
    top_hiring = db.query(
        models.Company.name,
        func.count(models.PlacementExperience.id).label("hires_count")
    ).join(models.PlacementExperience).filter(
        models.PlacementExperience.is_approved == True,
        models.PlacementExperience.result == "Selected"
    ).group_by(models.Company.name).order_by(desc("hires_count")).limit(5).all()
    
    top_hiring_list = [{"company": r[0], "count": r[1]} for r in top_hiring]
    
    # 3. Department Wise Placements
    dept_placements = db.query(
        models.User.department,
        func.count(models.User.id).label("count")
    ).filter(
        models.User.placement_status == "placed",
        models.User.department != None
    ).group_by(models.User.department).all()
    
    dept_list = [{"department": r[0], "count": r[1]} for r in dept_placements]
    
    # 4. CTC packages overview (Average vs Highest per company)
    packages_overview = db.query(
        models.Company.name,
        models.Company.average_package,
        models.Company.highest_package
    ).filter(models.Company.average_package != None).order_by(desc(models.Company.highest_package)).limit(5).all()
    
    packages_list = [{"company": r[0], "average": r[1], "highest": r[2]} for r in packages_overview]
    
    # 5. Top Contributors (User posting most approved experiences / questions)
    top_contributors = db.query(
        models.User.username,
        func.count(models.PlacementExperience.id).label("posts_count")
    ).join(models.PlacementExperience).filter(
        models.PlacementExperience.is_approved == True
    ).group_by(models.User.username).order_by(desc("posts_count")).limit(5).all()
    
    contributors_list = [{"username": r[0], "count": r[1]} for r in top_contributors]
    
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
        "packages_overview": packages_list,
        "top_contributors": contributors_list
    }
