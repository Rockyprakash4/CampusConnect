from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class ReadRequest(BaseModel):
    notification_id: Optional[int] = None # None means mark all as read

@router.get("/", response_model=List[schemas.NotificationResponse])
def get_my_notifications(unread_only: bool = False, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.Notification).filter(models.Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    return query.order_by(models.Notification.created_at.desc()).all()

@router.get("/unread-count")
def get_unread_count(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    count = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read == False
    ).count()
    return {"unread_count": count}

@router.post("/read")
def mark_as_read(req: ReadRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if req.notification_id:
        notif = db.query(models.Notification).filter(
            models.Notification.id == req.notification_id,
            models.Notification.user_id == current_user.id
        ).first()
        if notif:
            notif.is_read = True
            db.commit()
    else:
        db.query(models.Notification).filter(
            models.Notification.user_id == current_user.id,
            models.Notification.is_read == False
        ).update({"is_read": True}, synchronize_session=False)
        db.commit()
        
    return {"message": "Notifications updated"}
