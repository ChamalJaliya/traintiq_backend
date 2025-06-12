from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app import db

class Profile(db.Model):
    """Model for generated profiles"""
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Generated profile content
    custom_instructions = Column(Text)  # User's custom instructions
    
    # Metadata
    status = Column(String(50), default='pending')  # pending, processing, completed, failed
    profile_type = Column(String(100))  # job_profile, project_profile, etc.
    generated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI Processing metadata
    processing_metadata = Column(JSON)  # Store AI processing details
    confidence_score = Column(Float)  # AI confidence in the generated profile
    
    # Relationships
    documents = relationship("ProfileDocument", back_populates="profile", cascade="all, delete-orphan")
    template_id = Column(Integer, ForeignKey('profile_templates.id'))
    template = relationship("ProfileTemplate", back_populates="profiles")


class ProfileDocument(db.Model):
    """Model for documents uploaded for profile generation"""
    __tablename__ = 'profile_documents'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    file_size = Column(Integer)
    
    # Extracted content
    extracted_content = Column(Text)
    extraction_metadata = Column(JSON)  # Store extraction details
    
    # Processing status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("Profile", back_populates="documents")


class ProfileTemplate(db.Model):
    """Model for profile generation templates"""
    __tablename__ = 'profile_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Template configuration
    template_type = Column(String(100), nullable=False)  # job_profile, project_profile, etc.
    prompt_template = Column(Text, nullable=False)  # LangChain prompt template
    system_instructions = Column(Text)  # System-level instructions for AI
    
    # Template settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration JSON for advanced settings
    configuration = Column(JSON)  # Store additional template configurations
    
    # Relationships
    profiles = relationship("Profile", back_populates="template")


class ProfileEmbedding(db.Model):
    """Model for storing profile embeddings for semantic search"""
    __tablename__ = 'profile_embeddings'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'), nullable=False)
    
    # Embedding data
    embedding_vector = Column(JSON, nullable=False)  # Store as JSON array
    embedding_model = Column(String(100), nullable=False)  # Model used for embedding
    
    # Content metadata
    content_type = Column(String(50))  # full_profile, summary, keywords
    content_hash = Column(String(64))  # Hash of content for change detection
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Index for efficient similarity search
    __table_args__ = {'extend_existing': True} 