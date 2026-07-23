from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models, schemas, auth
from utils import cloudinary_helper

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])

@router.get("/", response_model=List[schemas.RoadmapResponse])
def list_roadmaps(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Roadmap)
    if search:
        query = query.filter(
            models.Roadmap.title.ilike(f"%{search}%") |
            models.Roadmap.target_role.ilike(f"%{search}%") |
            models.Roadmap.target_company.ilike(f"%{search}%") |
            models.Roadmap.topics.ilike(f"%{search}%")
        )
    return query.order_by(models.Roadmap.created_at.desc()).all()

@router.post("/", response_model=schemas.RoadmapResponse)
def create_roadmap(req: schemas.RoadmapCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_roadmap = models.Roadmap(
        **req.model_dump(),
        user_id=current_user.id
    )
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)
    return db_roadmap

@router.post("/{roadmap_id}/notes")
def upload_roadmap_notes(roadmap_id: int, file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
        
    if current_user.role != "admin" and roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this roadmap")
        
    url = cloudinary_helper.upload_image_or_file(file, folder="roadmaps")
    roadmap.pdf_notes_url = url
    db.commit()
    return {"pdf_notes_url": url, "message": "Roadmap notes uploaded successfully"}

@router.delete("/{roadmap_id}")
def delete_roadmap(roadmap_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
        
    if current_user.role != "admin" and roadmap.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this roadmap")
        
    db.delete(roadmap)
    db.commit()
    return {"message": "Roadmap deleted successfully"}
