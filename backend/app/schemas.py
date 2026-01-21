"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from enum import Enum


# Enums
class SubmissionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"


class DirectoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    NEEDS_UPDATE = "needs_update"


# ============ SaaS Product Schemas ============

class SaaSProductBase(BaseModel):
    """Base schema for SaaS product"""
    name: str = Field(..., min_length=1, max_length=255)
    website_url: str = Field(..., min_length=1, max_length=512)
    tagline: Optional[str] = Field(None, max_length=255)
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: List[str] = []
    
    contact_email: EmailStr
    contact_name: Optional[str] = Field(None, max_length=255)
    
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    
    pricing_model: Optional[str] = Field(None, max_length=100)
    pricing_details: Optional[str] = None


class SaaSProductCreate(SaaSProductBase):
    """Schema for creating a SaaS product"""
    pass


class SaaSProductUpdate(BaseModel):
    """Schema for updating a SaaS product"""
    name: Optional[str] = Field(None, max_length=255)
    website_url: Optional[str] = Field(None, max_length=512)
    tagline: Optional[str] = Field(None, max_length=255)
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    
    twitter_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    
    pricing_model: Optional[str] = Field(None, max_length=100)
    pricing_details: Optional[str] = None
    is_active: Optional[bool] = None


class SaaSProductResponse(SaaSProductBase):
    """Schema for SaaS product response"""
    id: int
    logo_path: Optional[str] = None
    screenshot_paths: List[str] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SaaSProductWithStats(SaaSProductResponse):
    """Schema for SaaS product with submission stats"""
    total_submissions: int = 0
    pending_count: int = 0
    submitted_count: int = 0
    approved_count: int = 0
    failed_count: int = 0


# ============ Directory Schemas ============

class DirectoryBase(BaseModel):
    """Base schema for directory"""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=512)
    submission_url: Optional[str] = Field(None, max_length=512)
    category: Optional[str] = Field(None, max_length=100)
    domain_authority: Optional[int] = Field(None, ge=0, le=100)
    monthly_traffic: Optional[int] = Field(None, ge=0)
    requires_account: bool = False
    requires_approval: bool = True
    requires_payment: bool = False
    notes: Optional[str] = None


class DirectoryCreate(DirectoryBase):
    """Schema for creating a directory"""
    pass


class DirectoryUpdate(BaseModel):
    """Schema for updating a directory"""
    name: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=512)
    submission_url: Optional[str] = Field(None, max_length=512)
    category: Optional[str] = Field(None, max_length=100)
    domain_authority: Optional[int] = Field(None, ge=0, le=100)
    monthly_traffic: Optional[int] = Field(None, ge=0)
    requires_account: Optional[bool] = None
    requires_approval: Optional[bool] = None
    requires_payment: Optional[bool] = None
    status: Optional[DirectoryStatus] = None
    notes: Optional[str] = None


class DirectoryResponse(DirectoryBase):
    """Schema for directory response"""
    id: int
    status: DirectoryStatus
    form_schema: Optional[dict] = None
    last_checked_at: Optional[datetime] = None
    success_rate: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DirectoryBulkImport(BaseModel):
    """Schema for bulk importing directories"""
    directories: List[DirectoryCreate]


# ============ Submission Schemas ============

class SubmissionCreate(BaseModel):
    """Schema for creating a submission"""
    saas_product_id: int
    directory_id: int


class SubmissionBulkCreate(BaseModel):
    """Schema for bulk creating submissions"""
    saas_product_id: int
    directory_ids: List[int]


class SubmissionResponse(BaseModel):
    """Schema for submission response"""
    id: int
    saas_product_id: int
    directory_id: int
    status: SubmissionStatus
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    listing_url: Optional[str] = None
    attempt_count: int
    max_attempts: int
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    detected_fields: Optional[dict] = None
    filled_fields: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubmissionWithDetails(SubmissionResponse):
    """Schema for submission with related data"""
    saas_product: SaaSProductResponse
    directory: DirectoryResponse


class SubmissionLogEntry(BaseModel):
    """Schema for a log entry"""
    timestamp: datetime
    level: str
    message: str
    details: Optional[dict] = None


# ============ Queue Schemas ============

class QueueItemCreate(BaseModel):
    """Schema for adding to queue"""
    submission_id: int
    scheduled_at: datetime
    priority: int = 0


class QueueItemResponse(BaseModel):
    """Schema for queue item response"""
    id: int
    submission_id: int
    scheduled_at: datetime
    priority: int
    is_processed: bool
    processed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Dashboard Stats Schemas ============

class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_products: int
    total_directories: int
    total_submissions: int
    
    pending_submissions: int
    in_progress_submissions: int
    submitted_submissions: int
    approved_submissions: int
    failed_submissions: int
    
    success_rate: float
    submissions_today: int
    submissions_this_week: int


class SubmissionTrend(BaseModel):
    """Schema for submission trends"""
    date: str
    submitted: int
    approved: int
    failed: int


# ============ Form Detection Schemas ============

class FormField(BaseModel):
    """Schema for a detected form field"""
    name: str
    field_type: str  # text, email, url, textarea, select, file, checkbox
    label: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    selector: str  # CSS selector to locate the field
    options: Optional[List[str]] = None  # For select fields


class FormDetectionResult(BaseModel):
    """Schema for form detection result"""
    url: str
    form_found: bool
    form_selector: Optional[str] = None
    fields: List[FormField] = []
    submit_button_selector: Optional[str] = None
    screenshot_path: Optional[str] = None
    confidence: float = 0.0


# ============ API Response Wrappers ============

class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
