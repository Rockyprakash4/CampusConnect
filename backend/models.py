import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student") # student, placed student, admin
    
    register_number = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    batch = Column(String(20), nullable=True)
    college = Column(String(150), nullable=True)
    skills = Column(Text, nullable=True) # Comma-separated list
    github = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    resume_url = Column(String(255), nullable=True)
    profile_pic_url = Column(String(255), nullable=True)
    
    placement_status = Column(String(20), default="unplaced") # unplaced, placed
    company_name = Column(String(100), nullable=True)
    job_role = Column(String(100), nullable=True)
    ctc = Column(Float, nullable=True) # CTC in LPA
    
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    experiences = relationship("PlacementExperience", back_populates="author", cascade="all, delete-orphan")
    questions = relationship("InterviewQuestion", back_populates="author", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="author", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="author", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="author", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    logo_url = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    average_package = Column(Float, nullable=True) # in LPA
    highest_package = Column(Float, nullable=True) # in LPA
    eligibility = Column(Text, nullable=True)
    selection_process = Column(Text, nullable=True)
    hiring_pattern = Column(Text, nullable=True)
    faq = Column(Text, nullable=True) # JSON or markdown string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    experiences = relationship("PlacementExperience", back_populates="company", cascade="all, delete-orphan")
    questions = relationship("InterviewQuestion", back_populates="company", cascade="all, delete-orphan")


class PlacementExperience(Base):
    __tablename__ = "placement_experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    job_role = Column(String(100), nullable=False)
    ctc = Column(Float, nullable=False) # in LPA
    job_type = Column(String(50), default="Full-Time") # Internship, Full-Time, Internship + Full-Time
    location = Column(String(100), nullable=True)
    drive_date = Column(String(30), nullable=True) # Store date as string or Date
    hiring_type = Column(String(50), default="On Campus") # On Campus, Off Campus, Pool Campus
    eligibility_criteria = Column(Text, nullable=True)
    rounds_count = Column(Integer, default=1)
    difficulty = Column(String(20), default="Medium") # Easy, Medium, Hard
    result = Column(String(20), default="Selected") # Selected, Rejected
    
    # Detailed parts
    experience_details = Column(Text, nullable=False)
    prep_strategy = Column(Text, nullable=True)
    prep_timeline = Column(Text, nullable=True)
    coding_round_exp = Column(Text, nullable=True)
    tech_questions = Column(Text, nullable=True)
    hr_questions = Column(Text, nullable=True)
    behavioral_questions = Column(Text, nullable=True)
    sql_questions = Column(Text, nullable=True)
    system_design_questions = Column(Text, nullable=True)
    mistakes = Column(Text, nullable=True)
    tips = Column(Text, nullable=True)
    resources_used = Column(Text, nullable=True)
    leetcode_solved = Column(Text, nullable=True)
    projects_asked = Column(Text, nullable=True)
    resume_tips = Column(Text, nullable=True)
    final_suggestions = Column(Text, nullable=True)
    
    attachment_url = Column(String(255), nullable=True)
    tags = Column(String(255), nullable=True) # Comma-separated tags
    is_approved = Column(Boolean, default=False)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="experiences")
    company = relationship("Company", back_populates="experiences")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(String(100), nullable=False)
    category = Column(String(50), default="DSA") # DSA, OOPS, DBMS, Operating System, Computer Networks, SQL, Java, Python, JavaScript, HTML, CSS, Bootstrap, HR, Aptitude
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    difficulty = Column(String(20), default="Medium") # Easy, Medium, Hard
    topic = Column(String(100), nullable=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="questions")
    company = relationship("Company", back_populates="questions")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    target_company = Column(String(100), nullable=True)
    target_role = Column(String(100), nullable=True)
    duration = Column(String(50), nullable=True) # e.g. 3 Months
    daily_plan = Column(Text, nullable=True)
    weekly_plan = Column(Text, nullable=True)
    topics = Column(Text, nullable=True)
    resources = Column(Text, nullable=True)
    youtube_links = Column(Text, nullable=True)
    pdf_notes_url = Column(String(255), nullable=True)
    leetcode_sheet = Column(Text, nullable=True)
    gfg_links = Column(Text, nullable=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="roadmaps")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_type = Column(String(20), nullable=False) # experience, question, roadmap
    parent_id = Column(Integer, nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_type = Column(String(20), nullable=False) # experience, question, roadmap
    parent_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="likes")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_type = Column(String(20), nullable=False) # experience, question, roadmap
    parent_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="bookmarks")


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Recipient
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Triggerer
    type = Column(String(20), nullable=False) # like, comment, follow, post_approval, admin_alert
    parent_type = Column(String(20), nullable=True) # experience, question, roadmap, user
    parent_id = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    recipient = relationship("User", foreign_keys=[user_id])
    actor = relationship("User", foreign_keys=[actor_id])


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Reporter
    parent_type = Column(String(20), nullable=False) # experience, question, roadmap, comment
    parent_id = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(String(20), default="Pending") # Pending, Resolved, Dismissed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="reports")
