from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class ProfileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProfileType(str, Enum):
    JOB_PROFILE = "job_profile"
    PROJECT_PROFILE = "project_profile"
    COMPANY_PROFILE = "company_profile"
    SKILLS_PROFILE = "skills_profile"
    CUSTOM = "custom"

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

# Request Schemas
class ProfileCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    profile_type: ProfileType = Field(default=ProfileType.CUSTOM)
    custom_instructions: Optional[str] = None
    template_id: Optional[int] = None

class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: FileType
    file_size: int
    uploaded_at: datetime

class ProfileTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_type: ProfileType
    prompt_template: str = Field(..., min_length=1)
    system_instructions: Optional[str] = None
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    configuration: Optional[Dict[str, Any]] = None

class ProfileUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    custom_instructions: Optional[str] = None
    template_id: Optional[int] = None

# Response Schemas
class ProfileDocumentResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_size: Optional[int]
    processed: bool
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ProfileTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template_type: str
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content: Optional[str]
    custom_instructions: Optional[str]
    status: ProfileStatus
    profile_type: str
    generated_at: datetime
    updated_at: datetime
    confidence_score: Optional[float]
    processing_metadata: Optional[Dict[str, Any]]
    documents: List[ProfileDocumentResponse] = []
    template: Optional[ProfileTemplateResponse]
    
    class Config:
        from_attributes = True

class ProfileListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: ProfileStatus
    profile_type: str
    generated_at: datetime
    confidence_score: Optional[float]
    document_count: int = 0
    
    class Config:
        from_attributes = True

class ProfileGenerationRequest(BaseModel):
    profile_id: int
    force_regenerate: bool = Field(default=False)

class ProfileSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    profile_type: Optional[ProfileType] = None
    limit: int = Field(default=10, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class ProfileSearchResult(BaseModel):
    id: int
    title: str
    description: Optional[str]
    profile_type: str
    similarity_score: float
    generated_at: datetime
    
class ProfileSearchResponse(BaseModel):
    results: List[ProfileSearchResult]
    total_count: int
    query: str

# Bulk operation schemas
class BulkProfileGenerationRequest(BaseModel):
    profile_ids: List[int] = Field(..., min_items=1, max_items=50)
    force_regenerate: bool = Field(default=False)

class BulkOperationResponse(BaseModel):
    success_count: int
    failed_count: int
    task_ids: List[str]  # Celery task IDs
    message: str

# Analytics schemas
class ProfileAnalytics(BaseModel):
    total_profiles: int
    profiles_by_status: Dict[str, int]
    profiles_by_type: Dict[str, int]
    average_confidence_score: Optional[float]
    processing_success_rate: float 