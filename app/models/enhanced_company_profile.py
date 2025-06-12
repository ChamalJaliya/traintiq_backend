"""
Enhanced Company Profile Database Model
Supports sophisticated profile generation with AI metadata and structured data
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

Base = declarative_base()

class EnhancedCompanyProfile(Base):
    """Enhanced company profile model with AI-generated content and metadata"""
    
    __tablename__ = 'enhanced_company_profiles'
    
    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Profile content
    company_name = Column(String(255), index=True)
    industry = Column(String(100), index=True)
    founded_date = Column(String(50))
    headquarters = Column(String(255))
    
    # AI-generated content
    executive_summary = Column(Text)
    company_overview = Column(Text)
    products_services = Column(Text)
    leadership_team = Column(Text)
    recent_developments = Column(Text)
    market_position = Column(Text)
    competitive_analysis = Column(Text)
    full_profile = Column(Text, nullable=False)
    
    # Structured data (JSON fields)
    key_people = Column(JSON)  # List of key personnel with roles
    financial_data = Column(JSON)  # Financial information extracted
    technology_stack = Column(JSON)  # Technologies used by the company
    contact_information = Column(JSON)  # Contact details
    social_media_presence = Column(JSON)  # Social media URLs and metrics
    
    # Generation metadata
    confidence_score = Column(Float, default=0.0, index=True)
    generation_time = Column(Float)  # Time taken to generate in seconds
    sources_processed = Column(Integer, default=0)
    total_content_length = Column(Integer, default=0)
    entities_extracted = Column(Integer, default=0)
    
    # Source information
    source_urls = Column(JSON)  # List of URLs used
    source_documents = Column(JSON)  # Document metadata
    custom_instructions = Column(Text)
    focus_areas = Column(JSON)  # Areas of focus during generation
    
    # Processing details
    model_used = Column(String(50), default='gpt-4-turbo-preview')
    processing_pipeline = Column(String(50), default='enhanced_v2.0')
    prompt_template = Column(String(100))
    cache_used = Column(Boolean, default=False)
    
    # Quality metrics
    completeness_score = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    
    # Status and timestamps
    status = Column(String(20), default='processing', index=True)  # processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Error handling
    error_message = Column(Text)
    warnings = Column(JSON)  # List of warnings during generation
    
    # Enhanced features
    template_used = Column(String(50))  # Template type used for generation
    enhancement_applied = Column(Boolean, default=False)
    version = Column(String(20), default='2.0')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'generation_id': self.generation_id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'industry': self.industry,
            'founded_date': self.founded_date,
            'headquarters': self.headquarters,
            'profile_content': {
                'executive_summary': self.executive_summary,
                'company_overview': self.company_overview,
                'products_services': self.products_services,
                'leadership_team': self.leadership_team,
                'recent_developments': self.recent_developments,
                'market_position': self.market_position,
                'competitive_analysis': self.competitive_analysis,
                'full_profile': self.full_profile
            },
            'structured_data': {
                'key_people': self.key_people,
                'financial_data': self.financial_data,
                'technology_stack': self.technology_stack,
                'contact_information': self.contact_information,
                'social_media_presence': self.social_media_presence
            },
            'metadata': {
                'confidence_score': self.confidence_score,
                'generation_time': self.generation_time,
                'sources_processed': self.sources_processed,
                'total_content_length': self.total_content_length,
                'entities_extracted': self.entities_extracted,
                'model_used': self.model_used,
                'processing_pipeline': self.processing_pipeline,
                'cache_used': self.cache_used,
                'quality_metrics': {
                    'completeness_score': self.completeness_score,
                    'accuracy_score': self.accuracy_score,
                    'clarity_score': self.clarity_score,
                    'relevance_score': self.relevance_score
                }
            },
            'generation_info': {
                'source_urls': self.source_urls,
                'source_documents': self.source_documents,
                'custom_instructions': self.custom_instructions,
                'focus_areas': self.focus_areas,
                'template_used': self.template_used,
                'enhancement_applied': self.enhancement_applied
            },
            'status': {
                'status': self.status,
                'progress': self.progress,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'error_message': self.error_message,
                'warnings': self.warnings
            },
            'version': self.version
        }
    
    @classmethod
    def from_generation_result(
        cls,
        generation_id: str,
        user_id: int,
        result: Dict[str, Any],
        metadata: Dict[str, Any],
        generation_request: Dict[str, Any]
    ) -> 'EnhancedCompanyProfile':
        """Create profile from generation result"""
        
        profile_data = result.get('profile', {})
        structured_data = metadata.get('structured_data', {})
        
        return cls(
            generation_id=generation_id,
            user_id=user_id,
            company_name=structured_data.get('company_name', ''),
            industry=structured_data.get('industry', ''),
            founded_date=structured_data.get('founded', ''),
            headquarters=structured_data.get('headquarters', ''),
            
            # AI-generated content
            executive_summary=profile_data.get('executive_summary', ''),
            company_overview=profile_data.get('company_overview', ''),
            products_services=profile_data.get('products_services', ''),
            leadership_team=profile_data.get('leadership_team', ''),
            recent_developments=profile_data.get('recent_developments', ''),
            market_position=profile_data.get('market_position', ''),
            competitive_analysis=profile_data.get('competitive_analysis', ''),
            full_profile=profile_data.get('full_profile', ''),
            
            # Structured data
            key_people=structured_data.get('key_people', []),
            financial_data=structured_data.get('financial_data', {}),
            technology_stack=structured_data.get('technology_stack', []),
            contact_information=structured_data.get('contact_info', {}),
            social_media_presence=structured_data.get('social_media', {}),
            
            # Generation metadata
            confidence_score=metadata.get('confidence_score', 0.0),
            generation_time=metadata.get('generation_time', 0.0),
            sources_processed=metadata.get('sources_processed', 0),
            total_content_length=metadata.get('total_content_length', 0),
            entities_extracted=metadata.get('entities_extracted', 0),
            model_used=metadata.get('model_used', 'gpt-4-turbo-preview'),
            processing_pipeline=metadata.get('processing_pipeline', 'enhanced_v2.0'),
            cache_used=metadata.get('cache_hits', 0) > 0,
            
            # Source information
            source_urls=generation_request.get('urls', []),
            source_documents=generation_request.get('document_metadata', []),
            custom_instructions=generation_request.get('custom_instructions', ''),
            focus_areas=generation_request.get('focus_areas', []),
            template_used=generation_request.get('template', ''),
            
            status='completed',
            progress=100,
            completed_at=datetime.utcnow()
        )
    
    def update_quality_scores(self, quality_metrics: Dict[str, float]):
        """Update quality assessment scores"""
        self.completeness_score = quality_metrics.get('completeness_score', 0.0)
        self.accuracy_score = quality_metrics.get('accuracy_score', 0.0)
        self.clarity_score = quality_metrics.get('clarity_score', 0.0)
        self.relevance_score = quality_metrics.get('relevance_score', 0.0)
        self.updated_at = datetime.utcnow()

class ProfileGenerationJob(Base):
    """Model for tracking profile generation jobs"""
    
    __tablename__ = 'profile_generation_jobs'
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    profile_id = Column(Integer, ForeignKey('enhanced_company_profiles.id'), nullable=True)
    
    # Job details
    job_type = Column(String(50), default='single')  # single, batch, enhancement
    priority = Column(String(20), default='normal')  # normal, high, urgent
    
    # Request data
    request_data = Column(JSON, nullable=False)
    
    # Job status
    status = Column(String(20), default='queued', index=True)  # queued, running, completed, failed
    progress = Column(Integer, default=0)
    current_step = Column(String(100))
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, index=True)
    completed_at = Column(DateTime, index=True)
    estimated_completion = Column(DateTime, index=True)
    
    # Results and errors
    result_data = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relationships
    profile = relationship("EnhancedCompanyProfile", backref="generation_job")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'user_id': self.user_id,
            'profile_id': self.profile_id,
            'job_type': self.job_type,
            'priority': self.priority,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }

class ProfileTemplate(Base):
    """Model for storing profile generation templates"""
    
    __tablename__ = 'profile_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    template_key = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Template configuration
    focus_areas = Column(JSON)  # List of focus areas
    custom_instructions = Column(Text)
    prompt_template = Column(Text)
    
    # Template metadata
    category = Column(String(50))  # startup, enterprise, technology, etc.
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer)  # user who created the template
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    avg_confidence_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'id': self.id,
            'template_key': self.template_key,
            'name': self.name,
            'description': self.description,
            'focus_areas': self.focus_areas,
            'custom_instructions': self.custom_instructions,
            'category': self.category,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'avg_confidence_score': self.avg_confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProfileAnalytics(Base):
    """Model for tracking profile generation analytics"""
    
    __tablename__ = 'profile_analytics'
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey('enhanced_company_profiles.id'), nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Analytics data
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    edit_count = Column(Integer, default=0)
    
    # User interactions
    last_viewed = Column(DateTime)
    last_downloaded = Column(DateTime)
    last_shared = Column(DateTime)
    last_edited = Column(DateTime)
    
    # Quality feedback
    user_rating = Column(Float)  # 1-5 stars
    user_feedback = Column(Text)
    
    # Performance metrics
    load_time = Column(Float)  # Time to load/display
    export_formats = Column(JSON)  # Formats the profile was exported to
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship("EnhancedCompanyProfile", backref="analytics")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics to dictionary"""
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'user_id': self.user_id,
            'interactions': {
                'view_count': self.view_count,
                'download_count': self.download_count,
                'share_count': self.share_count,
                'edit_count': self.edit_count
            },
            'last_activity': {
                'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
                'last_downloaded': self.last_downloaded.isoformat() if self.last_downloaded else None,
                'last_shared': self.last_shared.isoformat() if self.last_shared else None,
                'last_edited': self.last_edited.isoformat() if self.last_edited else None
            },
            'feedback': {
                'user_rating': self.user_rating,
                'user_feedback': self.user_feedback
            },
            'performance': {
                'load_time': self.load_time,
                'export_formats': self.export_formats
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 