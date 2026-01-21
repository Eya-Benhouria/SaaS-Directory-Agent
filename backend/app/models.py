"""
Database Models for SaaS Directory Submission Agent
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from enum import Enum
from .database import Base


class SubmissionStatus(str, Enum):
    """Status of a directory submission"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class DirectoryStatus(str, Enum):
    """Status of a directory in the system"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    NEEDS_UPDATE = "needs_update"


class SaaSProduct(Base):
    """SaaS product to be submitted to directories"""
    __tablename__ = "saas_products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    website_url = Column(String(512), nullable=False)
    tagline = Column(String(255), nullable=True)
    short_description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)  # List of tags
    
    # Contact info
    contact_email = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    
    # Social links
    twitter_url = Column(String(512), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    github_url = Column(String(512), nullable=True)
    
    # Media
    logo_path = Column(String(512), nullable=True)
    screenshot_paths = Column(JSON, default=list)  # List of screenshot paths
    
    # Pricing
    pricing_model = Column(String(100), nullable=True)  # free, freemium, paid
    pricing_details = Column(Text, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("DirectorySubmission", back_populates="saas_product", cascade="all, delete-orphan")


class Directory(Base):
    """Directory website where SaaS can be submitted"""
    __tablename__ = "directories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(512), nullable=False, unique=True)
    submission_url = Column(String(512), nullable=True)  # Direct link to submission form
    
    # Directory metadata
    category = Column(String(100), nullable=True)
    domain_authority = Column(Integer, nullable=True)  # 0-100
    monthly_traffic = Column(Integer, nullable=True)
    
    # Form detection data (cached from LLM analysis)
    form_schema = Column(JSON, nullable=True)  # Detected form fields
    
    # Submission requirements
    requires_account = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    requires_payment = Column(Boolean, default=False)
    
    # Status and tracking
    status = Column(SQLEnum(DirectoryStatus), default=DirectoryStatus.ACTIVE)
    last_checked_at = Column(DateTime, nullable=True)
    success_rate = Column(Integer, default=0)  # 0-100
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = relationship("DirectorySubmission", back_populates="directory", cascade="all, delete-orphan")


class DirectorySubmission(Base):
    """Track individual submission attempts"""
    __tablename__ = "directory_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    saas_product_id = Column(Integer, ForeignKey("saas_products.id"), nullable=False)
    directory_id = Column(Integer, ForeignKey("directories.id"), nullable=False)
    
    # Submission status
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    
    # Tracking
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    listing_url = Column(String(512), nullable=True)  # URL of the approved listing
    
    # Attempt tracking
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    last_attempt_at = Column(DateTime, nullable=True)
    
    # Logs and errors
    submission_log = Column(JSON, default=list)  # List of log entries
    error_message = Column(Text, nullable=True)
    screenshot_path = Column(String(512), nullable=True)  # Screenshot of submission
    
    # AI Detection results
    detected_fields = Column(JSON, nullable=True)  # Fields found by AI
    filled_fields = Column(JSON, nullable=True)  # Fields that were filled
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saas_product = relationship("SaaSProduct", back_populates="submissions")
    directory = relationship("Directory", back_populates="submissions")


class SubmissionQueue(Base):
    """Queue for scheduled submissions"""
    __tablename__ = "submission_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("directory_submissions.id"), nullable=False)
    
    # Scheduling
    scheduled_at = Column(DateTime, nullable=False)
    priority = Column(Integer, default=0)  # Higher = more priority
    
    # Status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("DirectorySubmission")


class ActivityLog(Base):
    """Log all system activities"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Activity details
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)  # saas_product, directory, submission
    entity_id = Column(Integer, nullable=True)
    
    # Log data
    message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    # Severity
    level = Column(String(20), default="info")  # debug, info, warning, error
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
