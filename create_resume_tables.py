#!/usr/bin/env python3
"""
Database migration script for Resume Builder feature
Creates all necessary tables for the resume builder functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app import create_app, db
from app.models.resume import Resume, ResumeSection, ExtractionJob, ResumeTemplate, ResumeGeneration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all resume-related tables"""
    app = create_app()
    
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

def drop_tables():
    """Drop all resume-related tables (for development only)"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.warning("Dropping resume builder tables...")
            
            # Drop tables in reverse order to handle foreign keys
            db.drop_all()
            
            logger.warning("Resume builder tables dropped!")
            
        except Exception as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            raise

def reset_database():
    """Drop and recreate all tables"""
    logger.info("Resetting resume builder database...")
    drop_tables()
    create_tables()
    logger.info("Database reset completed!")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Resume Builder Database Migration')
    parser.add_argument('action', choices=['create', 'drop', 'reset'], 
                       help='Action to perform: create, drop, or reset tables')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_tables()
    elif args.action == 'drop':
        drop_tables()
    elif args.action == 'reset':
        reset_database()
    
    print(f"Migration action '{args.action}' completed successfully!") 