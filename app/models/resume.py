from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .. import db

class Resume(db.Model):
    """
    Model for storing uploaded resume files and metadata
    """
    __tablename__ = 'resumes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)  # Will add FK when User model exists
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    
    # Processing status
    status = Column(String(50), nullable=False, default='uploaded')
    # Status values: uploaded, extracting, extracted, extraction_failed, processing, completed, error
    
    # Extraction information
    current_extraction_id = Column(String(36), nullable=True)
    extracted_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Timestamps
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=True)
    
    # Additional metadata
    resume_metadata = Column(JSON, nullable=True)
    
    # Relationships
    sections = relationship("ResumeSection", back_populates="resume", cascade="all, delete-orphan")
    extraction_jobs = relationship("ExtractionJob", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Resume {self.id}: {self.original_filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'status': self.status,
            'confidence_score': self.confidence_score,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'resume_metadata': self.resume_metadata
        }

class ResumeSection(db.Model):
    """
    Model for storing extracted resume sections (experience, education, skills, etc.)
    """
    __tablename__ = 'resume_sections'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    
    # Section information
    section_name = Column(String(100), nullable=False)  # e.g., 'work_experience', 'education', 'skills'
    section_data = Column(JSON, nullable=False)
    
    # Quality metrics
    confidence_score = Column(Float, nullable=True)
    extraction_method = Column(String(50), nullable=True)  # 'ai', 'nlp', 'ner', 'manual'
    manually_edited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="sections")
    
    def __repr__(self):
        return f'<ResumeSection {self.id}: {self.section_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'section_name': self.section_name,
            'section_data': self.section_data,
            'confidence_score': self.confidence_score,
            'extraction_method': self.extraction_method,
            'manually_edited': self.manually_edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class ExtractionJob(db.Model):
    """
    Model for tracking AI extraction jobs and their progress
    """
    __tablename__ = 'extraction_jobs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    user_id = Column(String(36), nullable=True)  # Will add FK when User model exists
    
    # Job configuration
    extraction_options = Column(JSON, nullable=False)
    
    # Progress tracking
    status = Column(String(50), nullable=False, default='queued')
    # Status values: queued, processing, completed, failed, cancelled
    
    current_stage = Column(String(100), nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    
    # Results
    extracted_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Performance metrics
    processing_time_seconds = Column(Float, nullable=True)
    tokens_processed = Column(Integer, nullable=True)
    api_calls_made = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    resume = relationship("Resume", back_populates="extraction_jobs")
    
    def __repr__(self):
        return f'<ExtractionJob {self.id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'user_id': self.user_id,
            'extraction_options': self.extraction_options,
            'status': self.status,
            'current_stage': self.current_stage,
            'progress': self.progress,
            'error_message': self.error_message,
            'processing_time_seconds': self.processing_time_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @property
    def duration_seconds(self):
        """Calculate job duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None

class ResumeTemplate(db.Model):
    """
    Model for storing resume templates and formatting options
    """
    __tablename__ = 'resume_templates'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template configuration
    template_type = Column(String(50), nullable=False)  # 'modern', 'classic', 'creative', 'ats-friendly'
    template_data = Column(JSON, nullable=False)  # CSS, HTML structure, etc.
    
    # Template metadata
    is_public = Column(Boolean, default=True)
    created_by = Column(String(36), nullable=True)  # Will add FK when User model exists
    tags = Column(JSON, nullable=True)  # Array of tags like ['tech', 'creative', 'executive']
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResumeTemplate {self.id}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_type': self.template_type,
            'is_public': self.is_public,
            'tags': self.tags,
            'usage_count': self.usage_count,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ResumeGeneration(db.Model):
    """
    Model for tracking generated resume documents
    """
    __tablename__ = 'resume_generations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    template_id = Column(String(36), ForeignKey('resume_templates.id'), nullable=False)
    user_id = Column(String(36), nullable=True)  # Will add FK when User model exists
    
    # Generation configuration
    format_type = Column(String(20), nullable=False)  # 'pdf', 'html', 'docx'
    generation_options = Column(JSON, nullable=True)
    
    # Output information
    output_filename = Column(String(255), nullable=True)
    output_path = Column(String(500), nullable=True)
    output_size = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='pending')
    # Status values: pending, generating, completed, failed
    
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    resume = relationship("Resume")
    template = relationship("ResumeTemplate")
    
    def __repr__(self):
        return f'<ResumeGeneration {self.id}: {self.format_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'template_id': self.template_id,
            'user_id': self.user_id,
            'format_type': self.format_type,
            'generation_options': self.generation_options,
            'output_filename': self.output_filename,
            'output_size': self.output_size,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        } 