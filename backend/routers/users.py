from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas, auth
from utils import cloudinary_helper

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_profile(profile_data: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Set fields
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
        
    # Auto-adjust role based on placement status
    if current_user.placement_status == "placed" and current_user.role == "student":
        current_user.role = "placed student"
    elif current_user.placement_status == "unplaced" and current_user.role == "placed student":
        current_user.role = "student"
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/upload-avatar")
def upload_avatar(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
        
    avatar_url = cloudinary_helper.upload_image_or_file(file, folder="avatars")
    current_user.profile_pic_url = avatar_url
    db.commit()
    return {"profile_pic_url": avatar_url, "message": "Avatar updated successfully"}

@router.post("/me/upload-resume")
def upload_resume(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are allowed")
        
    resume_url = cloudinary_helper.upload_image_or_file(file, folder="resumes")
    current_user.resume_url = resume_url
    db.commit()
    return {"resume_url": resume_url, "message": "Resume uploaded successfully"}

@router.get("/profile/{username}", response_model=schemas.UserResponse)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/follow/{target_user_id}")
def follow_user(target_user_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.id == target_user_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")
        
    target_user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User to follow not found")
        
    follow_entry = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.followed_id == target_user_id
    ).first()
    
    if follow_entry:
        # Unfollow
        db.delete(follow_entry)
        db.commit()
        return {"status": "unfollowed", "message": f"You unfollowed {target_user.username}"}
    else:
        # Follow
        new_follow = models.Follow(follower_id=current_user.id, followed_id=target_user_id)
        db.add(new_follow)
        
        # Trigger notification
        notif = models.Notification(
            user_id=target_user_id,
            actor_id=current_user.id,
            type="follow",
            parent_type="user",
            parent_id=current_user.id,
            message=f"{current_user.username} started following you."
        )
        db.add(notif)
        db.commit()
        return {"status": "followed", "message": f"You followed {target_user.username}"}

@router.get("/profile/{username}/status")
def get_follow_status(username: str, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    is_following = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.followed_id == user.id
    ).first() is not None
    
    followers_count = db.query(models.Follow).filter(models.Follow.followed_id == user.id).count()
    following_count = db.query(models.Follow).filter(models.Follow.follower_id == user.id).count()
    
    return {
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count
    }

@router.get("/me/portfolio")
def get_my_portfolio(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # Experiences shared by current user
    experiences = db.query(models.PlacementExperience).filter(
        models.PlacementExperience.user_id == current_user.id
    ).all()
    
    # Bookmarks of current user
    bookmarks = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id
    ).all()
    
    return {
        "shared_experiences_count": len(experiences),
        "bookmarks_count": len(bookmarks)
    }
