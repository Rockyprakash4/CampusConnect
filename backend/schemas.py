from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import datetime

# -----------------------------------------------------
# Token Schemas
# -----------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# -----------------------------------------------------
# User Schemas
# -----------------------------------------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    register_number: Optional[str] = None
    department: Optional[str] = None
    batch: Optional[str] = None
    college: Optional[str] = None
    skills: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    placement_status: Optional[str] = None # unplaced, placed
    company_name: Optional[str] = None
    job_role: Optional[str] = None
    ctc: Optional[float] = None

class UserMiniResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    profile_pic_url: Optional[str] = None

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int
    role: str
    register_number: Optional[str] = None
    department: Optional[str] = None
    batch: Optional[str] = None
    college: Optional[str] = None
    skills: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    resume_url: Optional[str] = None
    profile_pic_url: Optional[str] = None
    placement_status: str
    company_name: Optional[str] = None
    job_role: Optional[str] = None
    ctc: Optional[float] = None
    is_verified: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Company Schemas
# -----------------------------------------------------
class CompanyBase(BaseModel):
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    logo_url: Optional[str] = None
    average_package: Optional[float] = None
    highest_package: Optional[float] = None
    eligibility: Optional[str] = None
    selection_process: Optional[str] = None
    hiring_pattern: Optional[str] = None
    faq: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    logo_url: Optional[str] = None
    average_package: Optional[float] = None
    highest_package: Optional[float] = None
    eligibility: Optional[str] = None
    selection_process: Optional[str] = None
    hiring_pattern: Optional[str] = None
    faq: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Comment Schemas
# -----------------------------------------------------
class CommentCreate(BaseModel):
    parent_type: str # experience, question, roadmap
    parent_id: int
    comment_text: str

class CommentResponse(BaseModel):
    id: int
    user_id: int
    parent_type: str
    parent_id: int
    comment_text: str
    created_at: datetime.datetime
    author: UserMiniResponse

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Placement Experience Schemas
# -----------------------------------------------------
class PlacementExperienceCreate(BaseModel):
    company_name: str # Creates or links company
    job_role: str
    ctc: float
    job_type: str = "Full-Time"
    location: Optional[str] = None
    drive_date: Optional[str] = None
    hiring_type: str = "On Campus"
    eligibility_criteria: Optional[str] = None
    rounds_count: int = 1
    difficulty: str = "Medium"
    result: str = "Selected"
    
    # Detailed Sections
    experience_details: str
    prep_strategy: Optional[str] = None
    prep_timeline: Optional[str] = None
    coding_round_exp: Optional[str] = None
    tech_questions: Optional[str] = None
    hr_questions: Optional[str] = None
    behavioral_questions: Optional[str] = None
    sql_questions: Optional[str] = None
    system_design_questions: Optional[str] = None
    mistakes: Optional[str] = None
    tips: Optional[str] = None
    resources_used: Optional[str] = None
    leetcode_solved: Optional[str] = None
    projects_asked: Optional[str] = None
    resume_tips: Optional[str] = None
    final_suggestions: Optional[str] = None
    
    tags: Optional[str] = None

class PlacementExperienceResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    job_role: str
    ctc: float
    job_type: str
    location: Optional[str] = None
    drive_date: Optional[str] = None
    hiring_type: str
    eligibility_criteria: Optional[str] = None
    rounds_count: int
    difficulty: str
    result: str
    
    experience_details: str
    prep_strategy: Optional[str] = None
    prep_timeline: Optional[str] = None
    coding_round_exp: Optional[str] = None
    tech_questions: Optional[str] = None
    hr_questions: Optional[str] = None
    behavioral_questions: Optional[str] = None
    sql_questions: Optional[str] = None
    system_design_questions: Optional[str] = None
    mistakes: Optional[str] = None
    tips: Optional[str] = None
    resources_used: Optional[str] = None
    leetcode_solved: Optional[str] = None
    projects_asked: Optional[str] = None
    resume_tips: Optional[str] = None
    final_suggestions: Optional[str] = None
    
    attachment_url: Optional[str] = None
    tags: Optional[str] = None
    is_approved: bool
    likes_count: int
    comments_count: int
    created_at: datetime.datetime
    
    author: UserMiniResponse
    company: CompanyResponse

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Interview Question Schemas
# -----------------------------------------------------
class InterviewQuestionCreate(BaseModel):
    company_name: str
    role: str
    category: str
    question_text: str
    answer_text: Optional[str] = None
    difficulty: str = "Medium"
    topic: Optional[str] = None

class InterviewQuestionResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    role: str
    category: str
    question_text: str
    answer_text: Optional[str] = None
    difficulty: str
    topic: Optional[str] = None
    likes_count: int
    comments_count: int
    created_at: datetime.datetime
    
    author: UserMiniResponse
    company: CompanyResponse

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Roadmap Schemas
# -----------------------------------------------------
class RoadmapCreate(BaseModel):
    title: str
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    duration: Optional[str] = None
    daily_plan: Optional[str] = None
    weekly_plan: Optional[str] = None
    topics: Optional[str] = None
    resources: Optional[str] = None
    youtube_links: Optional[str] = None
    leetcode_sheet: Optional[str] = None
    gfg_links: Optional[str] = None

class RoadmapResponse(BaseModel):
    id: int
    user_id: int
    title: str
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    duration: Optional[str] = None
    daily_plan: Optional[str] = None
    weekly_plan: Optional[str] = None
    topics: Optional[str] = None
    resources: Optional[str] = None
    youtube_links: Optional[str] = None
    pdf_notes_url: Optional[str] = None
    leetcode_sheet: Optional[str] = None
    gfg_links: Optional[str] = None
    likes_count: int
    comments_count: int
    created_at: datetime.datetime
    
    author: UserMiniResponse

    class Config:
        from_attributes = True


# -----------------------------------------------------
# Follow & Notification & Report Schemas
# -----------------------------------------------------
class NotificationResponse(BaseModel):
    id: int
    type: str
    parent_type: Optional[str] = None
    parent_id: Optional[int] = None
    message: str
    is_read: bool
    created_at: datetime.datetime
    actor: UserMiniResponse

    class Config:
        from_attributes = True

class ReportCreate(BaseModel):
    parent_type: str
    parent_id: int
    reason: str
    details: Optional[str] = None

class ReportResponse(BaseModel):
    id: int
    user_id: int
    parent_type: str
    parent_id: int
    reason: str
    details: Optional[str] = None
    status: str
    created_at: datetime.datetime
    author: UserMiniResponse

    class Config:
        from_attributes = True
