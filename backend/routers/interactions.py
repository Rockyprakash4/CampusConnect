from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/interactions", tags=["Interactions"])

class LikeRequest(BaseModel):
    parent_type: str # experience, question, roadmap
    parent_id: int

class BookmarkRequest(BaseModel):
    parent_type: str # experience, question, roadmap
    parent_id: int

@router.post("/like")
def toggle_like(req: LikeRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    like_entry = db.query(models.Like).filter(
        models.Like.user_id == current_user.id,
        models.Like.parent_type == req.parent_type,
        models.Like.parent_id == req.parent_id
    ).first()
    
    parent_obj = None
    if req.parent_type == "experience":
        parent_obj = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == req.parent_id).first()
    elif req.parent_type == "question":
        parent_obj = db.query(models.InterviewQuestion).filter(models.InterviewQuestion.id == req.parent_id).first()
    elif req.parent_type == "roadmap":
        parent_obj = db.query(models.Roadmap).filter(models.Roadmap.id == req.parent_id).first()
        
    if not parent_obj:
        raise HTTPException(status_code=404, detail="Parent item not found")
        
    if like_entry:
        db.delete(like_entry)
        parent_obj.likes_count = max(0, parent_obj.likes_count - 1)
        db.commit()
        return {"status": "unliked", "likes_count": parent_obj.likes_count}
    else:
        new_like = models.Like(
            user_id=current_user.id,
            parent_type=req.parent_type,
            parent_id=req.parent_id
        )
        db.add(new_like)
        parent_obj.likes_count += 1
        
        # Trigger notification
        if parent_obj.user_id != current_user.id:
            db.add(models.Notification(
                user_id=parent_obj.user_id,
                actor_id=current_user.id,
                type="like",
                parent_type=req.parent_type,
                parent_id=req.parent_id,
                message=f"{current_user.username} liked your {req.parent_type}."
            ))
            
        db.commit()
        return {"status": "liked", "likes_count": parent_obj.likes_count}

@router.post("/bookmark")
def toggle_bookmark(req: BookmarkRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    bookmark_entry = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.parent_type == req.parent_type,
        models.Bookmark.parent_id == req.parent_id
    ).first()
    
    parent_obj = None
    if req.parent_type == "experience":
        parent_obj = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == req.parent_id).first()
    elif req.parent_type == "question":
        parent_obj = db.query(models.InterviewQuestion).filter(models.InterviewQuestion.id == req.parent_id).first()
    elif req.parent_type == "roadmap":
        parent_obj = db.query(models.Roadmap).filter(models.Roadmap.id == req.parent_id).first()
        
    if not parent_obj:
        raise HTTPException(status_code=404, detail="Parent item not found")
        
    if bookmark_entry:
        db.delete(bookmark_entry)
        db.commit()
        return {"status": "unbookmarked", "message": "Removed from bookmarks"}
    else:
        new_bookmark = models.Bookmark(
            user_id=current_user.id,
            parent_type=req.parent_type,
            parent_id=req.parent_id
        )
        db.add(new_bookmark)
        db.commit()
        return {"status": "bookmarked", "message": "Saved to bookmarks"}

@router.post("/comment", response_model=schemas.CommentResponse)
def add_comment(req: schemas.CommentCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    parent_obj = None
    if req.parent_type == "experience":
        parent_obj = db.query(models.PlacementExperience).filter(models.PlacementExperience.id == req.parent_id).first()
    elif req.parent_type == "question":
        parent_obj = db.query(models.InterviewQuestion).filter(models.InterviewQuestion.id == req.parent_id).first()
    elif req.parent_type == "roadmap":
        parent_obj = db.query(models.Roadmap).filter(models.Roadmap.id == req.parent_id).first()
        
    if not parent_obj:
        raise HTTPException(status_code=404, detail="Parent item not found")
        
    db_comment = models.Comment(
        user_id=current_user.id,
        parent_type=req.parent_type,
        parent_id=req.parent_id,
        comment_text=req.comment_text
    )
    db.add(db_comment)
    parent_obj.comments_count += 1
    
    # Notify author
    if parent_obj.user_id != current_user.id:
        db.add(models.Notification(
            user_id=parent_obj.user_id,
            actor_id=current_user.id,
            type="comment",
            parent_type=req.parent_type,
            parent_id=req.parent_id,
            message=f"{current_user.username} commented on your {req.parent_type}."
        ))
        
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/comments/{parent_type}/{parent_id}", response_model=List[schemas.CommentResponse])
def get_comments(parent_type: str, parent_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(
        models.Comment.parent_type == parent_type,
        models.Comment.parent_id == parent_id
    ).order_by(models.Comment.created_at.asc()).all()

@router.post("/report", response_model=schemas.ReportResponse)
def file_report(req: schemas.ReportCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_report = models.Report(
        user_id=current_user.id,
        parent_type=req.parent_type,
        parent_id=req.parent_id,
        reason=req.reason,
        details=req.details
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report
