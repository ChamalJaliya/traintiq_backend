#!/usr/bin/env python3
"""
Simple Database Migration Script for Resume Builder
Creates only the resume tables without loading the full application
"""

import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app with minimal configuration
app = Flask(__name__)

# Database configuration
DATABASE_URL = "mysql+pymysql://root:@localhost/traintiq_db"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define the models directly here to avoid import issues
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False, default='uploaded')
    current_extraction_id = Column(String(36), nullable=True)
    extracted_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=True)
    resume_metadata = Column(JSON, nullable=True)

class ResumeSection(db.Model):
    __tablename__ = 'resume_sections'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    section_name = Column(String(100), nullable=False)
    section_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    extraction_method = Column(String(50), nullable=True)
    manually_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

class ExtractionJob(db.Model):
    __tablename__ = 'extraction_jobs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    user_id = Column(String(36), nullable=True)
    extraction_options = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, default='queued')
    current_stage = Column(String(100), nullable=True)
    progress = Column(Integer, default=0)
    extracted_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    tokens_processed = Column(Integer, nullable=True)
    api_calls_made = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class ResumeTemplate(db.Model):
    __tablename__ = 'resume_templates'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)
    template_data = Column(JSON, nullable=False)
    is_public = Column(Boolean, default=True)
    created_by = Column(String(36), nullable=True)
    tags = Column(JSON, nullable=True)
    usage_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ResumeGeneration(db.Model):
    __tablename__ = 'resume_generations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey('resumes.id'), nullable=False)
    template_id = Column(String(36), ForeignKey('resume_templates.id'), nullable=False)
    user_id = Column(String(36), nullable=True)
    format_type = Column(String(20), nullable=False)
    generation_options = Column(JSON, nullable=True)
    output_filename = Column(String(255), nullable=True)
    output_path = Column(String(500), nullable=True)
    output_size = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default='pending')
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

def create_tables():
    """Create all resume-related tables"""
    with app.app_context():
        try:
            logger.info("Creating resume builder tables...")
            
            # Create tables
            db.create_all()
            
            logger.info("Resume builder tables created successfully!")
            
            # Create default resume templates
            create_default_templates()
            
            logger.info("Database migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise

def create_default_templates():
    """Create default resume templates"""
    try:
        logger.info("Creating default resume templates...")
        
        templates = [
            {
                'name': 'Modern Professional',
                'description': 'A clean, modern template perfect for tech and business professionals',
                'template_type': 'modern',
                'template_data': {
                    'layout': 'single-column',
                    'color_scheme': 'blue-gradient',
                    'font_family': 'Inter',
                    'sections': ['header', 'summary', 'experience', 'education', 'skills', 'projects']
                },
                'tags': ['tech', 'professional', 'modern', 'ats-friendly'],
                'is_public': True
            },
            {
                'name': 'Classic Executive',
                'description': 'Traditional format ideal for executive and senior management positions',
                'template_type': 'classic',
                'template_data': {
                    'layout': 'two-column',
                    'color_scheme': 'navy-corporate',
                    'font_family': 'Times New Roman',
                    'sections': ['header', 'summary', 'experience', 'education', 'achievements', 'skills']
                },
                'tags': ['executive', 'management', 'classic', 'corporate'],
                'is_public': True
            },
            {
                'name': 'Creative Portfolio',
                'description': 'Eye-catching design for creative professionals and designers',
                'template_type': 'creative',
                'template_data': {
                    'layout': 'asymmetric',
                    'color_scheme': 'purple-creative',
                    'font_family': 'Roboto',
                    'sections': ['header', 'portfolio', 'experience', 'skills', 'education', 'projects']
                },
                'tags': ['creative', 'design', 'portfolio', 'visual'],
                'is_public': True
            },
            {
                'name': 'ATS-Optimized',
                'description': 'Simple, clean format optimized for Applicant Tracking Systems',
                'template_type': 'ats-friendly',
                'template_data': {
                    'layout': 'single-column',
                    'color_scheme': 'minimal-black',
                    'font_family': 'Arial',
                    'sections': ['header', 'summary', 'experience', 'education', 'skills', 'certifications']
                },
                'tags': ['ats-friendly', 'simple', 'minimal', 'corporate'],
                'is_public': True
            }
        ]
        
        for template_data in templates:
            existing_template = ResumeTemplate.query.filter_by(name=template_data['name']).first()
            if not existing_template:
                template = ResumeTemplate(**template_data)
                db.session.add(template)
        
        db.session.commit()
        logger.info(f"Created {len(templates)} default resume templates")
        
    except Exception as e:
        logger.error(f"Failed to create default templates: {str(e)}")
        db.session.rollback()
        raise

if __name__ == '__main__':
    create_tables()
    print("Resume builder database migration completed successfully!") 