import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import datetime

from database import get_db
import models, schemas, auth
from utils import email_helper

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check email duplication
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")
    # Check username duplication
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username is already taken")
        
    hashed = auth.get_password_hash(user_in.password)
    v_token = auth.create_verification_token(user_in.email)
    
    # Auto-make first user Admin for convenience, else default to student
    role = "admin" if db.query(models.User).count() == 0 else "student"
    
    # DEV_MODE check to auto-verify
    dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
    is_verified = True if dev_mode else False
    
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed,
        role=role,
        is_verified=is_verified,
        verification_token=v_token if not is_verified else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    if not is_verified:
        email_helper.send_verification_email(db_user.email, db_user.username, v_token)
    return db_user

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    if not payload or payload.get("purpose") != "email_verification":
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.is_verified:
        return {"message": "Email is already verified"}
        
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully. You can now log in."}

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate by email or username
    user = db.query(models.User).filter(
        (models.User.username == form_data.username) | 
        (models.User.email == form_data.username)
    ).first()
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please verify your email address before logging in."
        )
        
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role, 
        "username": user.username
    }

@router.post("/forgot-password")
def forgot_password(req: schemas.ForgotPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        # Avoid user enumeration by sending generic response
        return {"message": "If the email exists, a password reset link has been sent."}
        
    reset_token = auth.create_reset_token(user.email)
    user.verification_token = reset_token # Reuse column to track reset token
    db.commit()
    
    email_helper.send_reset_password_email(user.email, user.username, reset_token)
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset-password")
def reset_password(req: schemas.ResetPassword, db: Session = Depends(get_db)):
    payload = auth.decode_token(req.token)
    if not payload or payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.hashed_password = auth.get_password_hash(req.new_password)
    user.verification_token = None
    db.commit()
    return {"message": "Password has been reset successfully. You can now log in."}

@router.post("/change-password")
def change_password(req: schemas.ChangePassword, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not auth.verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
        
    current_user.hashed_password = auth.get_password_hash(req.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
