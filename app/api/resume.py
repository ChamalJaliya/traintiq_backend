from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import uuid
import os
import asyncio
from datetime import datetime
from ..services.ai.resume_extraction_service import ResumeExtractionService
from ..services.data.file_processing_service import FileProcessingService
from ..models.resume import Resume, ResumeSection, ExtractionJob
from ..schemas.resume import ResumeSchema, ExtractionJobSchema
from .. import db
from ..core.decorators import login_required, json_required
from ..exceptions.api_exceptions import ValidationError, ProcessingError, NotFoundError

resume_bp = Blueprint('resume', __name__, url_prefix='/api/resume')

# Initialize services
extraction_service = ResumeExtractionService()
file_service = FileProcessingService()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route('/upload', methods=['POST'])
@login_required
def upload_resume():
    """
    Upload resume file and store for processing
    ---
    tags:
      - Resume Builder
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Resume file (PDF, DOC, DOCX)
      - name: type
        in: formData
        type: string
        required: false
        description: File type identifier
    responses:
      200:
        description: File uploaded successfully
        schema:
          type: object
          properties:
            file_id:
              type: string
              description: Unique file identifier
            filename:
              type: string
              description: Original filename
            file_size:
              type: integer
              description: File size in bytes
            upload_time:
              type: string
              format: date-time
              description: Upload timestamp
      400:
        description: Invalid file or request
      413:
        description: File too large
    """
    
    try:
        if 'file' not in request.files:
            raise ValidationError('No file provided')
        
        file = request.files['file']
        if file.filename == '':
            raise ValidationError('No file selected')
        
        if not allowed_file(file.filename):
            raise ValidationError('Invalid file type. Only PDF, DOC, and DOCX files are allowed.')
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        
        # Save file
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes')
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, f"{file_id}_{filename}")
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create resume record
        resume = Resume(
            id=file_id,
            user_id=request.current_user.id,
            original_filename=filename,
            file_path=file_path,
            file_size=file_size,
            upload_time=datetime.utcnow(),
            status='uploaded'
        )
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'file_id': file_id,
            'filename': filename,
            'file_size': file_size,
            'upload_time': resume.upload_time.isoformat(),
            'status': 'uploaded'
        }), 200
        
    except RequestEntityTooLarge:
        raise ValidationError('File too large. Maximum size is 10MB.')
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        raise ProcessingError('Failed to upload file')

@resume_bp.route('/extract/<file_id>', methods=['POST'])
@login_required
@json_required
def extract_resume_data(file_id):
    """
    Start AI-powered resume data extraction
    ---
    tags:
      - Resume Builder
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: Resume file ID
      - name: extraction_options
        in: body
        schema:
          type: object
          properties:
            use_nlp:
              type: boolean
              default: true
              description: Enable Natural Language Processing
            use_ner:
              type: boolean
              default: true
              description: Enable Named Entity Recognition
            use_ai_enhancement:
              type: boolean
              default: true
              description: Enable AI-powered enhancement
            extraction_templates:
              type: array
              items:
                type: string
              description: AI prompt templates to use
            custom_prompts:
              type: object
              description: Custom extraction prompts
    responses:
      200:
        description: Extraction started successfully
        schema:
          type: object
          properties:
            extraction_id:
              type: string
              description: Extraction job ID
            status:
              type: string
              description: Extraction status
            estimated_time:
              type: integer
              description: Estimated completion time in seconds
      404:
        description: Resume file not found
      400:
        description: Invalid extraction parameters
    """
    
    try:
        # Find resume record
        resume = Resume.query.filter_by(
            id=file_id, 
            user_id=request.current_user.id
        ).first()
        
        if not resume:
            raise NotFoundError('Resume file not found')
        
        if resume.status != 'uploaded':
            raise ValidationError('Resume is not ready for extraction')
        
        # Parse extraction options
        data = request.get_json()
        extraction_options = {
            'use_nlp': data.get('use_nlp', True),
            'use_ner': data.get('use_ner', True),
            'use_ai_enhancement': data.get('use_ai_enhancement', True),
            'extraction_templates': data.get('extraction_templates', [
                'comprehensive_profile',
                'professional_details',
                'skills_analysis',
                'experience_mapping'
            ]),
            'custom_prompts': data.get('custom_prompts', {}),
            'confidence_threshold': data.get('confidence_threshold', 0.7),
            'language': data.get('language', 'auto-detect')
        }
        
        # Create extraction job
        extraction_id = str(uuid.uuid4())
        extraction_job = ExtractionJob(
            id=extraction_id,
            resume_id=file_id,
            user_id=request.current_user.id,
            extraction_options=extraction_options,
            status='queued',
            created_at=datetime.utcnow()
        )
        
        db.session.add(extraction_job)
        
        # Update resume status
        resume.status = 'extracting'
        resume.current_extraction_id = extraction_id
        
        db.session.commit()
        
        # Start extraction process asynchronously
        asyncio.create_task(
            extraction_service.process_resume_extraction(
                extraction_id, resume.file_path, extraction_options
            )
        )
        
        return jsonify({
            'extraction_id': extraction_id,
            'status': 'started',
            'estimated_time': 60,  # 1 minute estimate
            'stages': [
                'Text Extraction',
                'NLP Processing', 
                'NER Analysis',
                'AI Enhancement',
                'Finalization'
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Extraction start error: {str(e)}")
        raise ProcessingError('Failed to start extraction')

@resume_bp.route('/extraction-status/<extraction_id>', methods=['GET'])
@login_required
def get_extraction_status(extraction_id):
    """
    Get extraction job status and progress
    ---
    tags:
      - Resume Builder
    parameters:
      - name: extraction_id
        in: path
        type: string
        required: true
        description: Extraction job ID
    responses:
      200:
        description: Extraction status retrieved
        schema:
          type: object
          properties:
            extraction_id:
              type: string
            status:
              type: string
              enum: [queued, processing, completed, failed]
            stage:
              type: string
              description: Current processing stage
            overall_progress:
              type: integer
              description: Overall progress percentage (0-100)
            stage_progress:
              type: integer
              description: Current stage progress percentage
            current_operation:
              type: string
              description: Current operation description
            extracted_sections:
              type: object
              description: Extracted data sections
            completed:
              type: boolean
              description: Whether extraction is complete
            error_message:
              type: string
              description: Error message if failed
      404:
        description: Extraction job not found
    """
    
    try:
        extraction_job = ExtractionJob.query.filter_by(
            id=extraction_id,
            user_id=request.current_user.id
        ).first()
        
        if not extraction_job:
            raise NotFoundError('Extraction job not found')
        
        # Get current progress from extraction service
        progress = extraction_service.get_extraction_progress(extraction_id)
        
        response_data = {
            'extraction_id': extraction_id,
            'status': extraction_job.status,
            'stage': progress.get('current_stage', 'Unknown'),
            'overall_progress': progress.get('overall_progress', 0),
            'stage_progress': progress.get('stage_progress', 0),
            'current_operation': progress.get('current_operation', ''),
            'completed': extraction_job.status in ['completed', 'failed'],
            'stage_changed': progress.get('stage_changed', False)
        }
        
        # Include extracted sections if available
        if extraction_job.status == 'completed' and extraction_job.extracted_data:
            response_data['extracted_sections'] = extraction_job.extracted_data
        
        # Include error message if failed
        if extraction_job.status == 'failed':
            response_data['error_message'] = extraction_job.error_message
        
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Status check error: {str(e)}")
        raise ProcessingError('Failed to get extraction status')

@resume_bp.route('/data/<file_id>', methods=['GET'])
@login_required
def get_resume_data(file_id):
    """
    Get extracted resume data
    ---
    tags:
      - Resume Builder  
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: Resume file ID
    responses:
      200:
        description: Resume data retrieved
        schema:
          type: object
          properties:
            resume_id:
              type: string
            filename:
              type: string
            extraction_status:
              type: string
            confidence_score:
              type: number
            extracted_data:
              type: object
              description: Structured resume data
            sections:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  data:
                    type: object
                  confidence:
                    type: number
                  last_updated:
                    type: string
                    format: date-time
      404:
        description: Resume not found
    """
    
    try:
        resume = Resume.query.filter_by(
            id=file_id,
            user_id=request.current_user.id
        ).first()
        
        if not resume:
            raise NotFoundError('Resume not found')
        
        # Get sections
        sections = ResumeSection.query.filter_by(resume_id=file_id).all()
        
        # Calculate overall confidence
        if sections:
            total_confidence = sum(s.confidence_score for s in sections if s.confidence_score)
            avg_confidence = total_confidence / len(sections) if sections else 0
        else:
            avg_confidence = 0
        
        return jsonify({
            'resume_id': file_id,
            'filename': resume.original_filename,
            'extraction_status': resume.status,
            'confidence_score': avg_confidence,
            'upload_time': resume.upload_time.isoformat(),
            'last_updated': resume.last_updated.isoformat() if resume.last_updated else None,
            'extracted_data': resume.extracted_data or {},
            'sections': [
                {
                    'name': section.section_name,
                    'data': section.section_data,
                    'confidence': section.confidence_score,
                    'last_updated': section.last_updated.isoformat()
                }
                for section in sections
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Data retrieval error: {str(e)}")
        raise ProcessingError('Failed to get resume data')

@resume_bp.route('/data/<file_id>', methods=['PUT'])
@login_required
@json_required
def update_resume_data(file_id):
    """
    Update extracted resume data
    ---
    tags:
      - Resume Builder
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: Resume file ID
      - name: resume_data
        in: body
        schema:
          type: object
          properties:
            sections:
              type: object
              description: Updated section data
            metadata:
              type: object
              description: Additional metadata
    responses:
      200:
        description: Resume data updated successfully
      404:
        description: Resume not found
      400:
        description: Invalid data format
    """
    
    try:
        resume = Resume.query.filter_by(
            id=file_id,
            user_id=request.current_user.id
        ).first()
        
        if not resume:
            raise NotFoundError('Resume not found')
        
        data = request.get_json()
        updated_sections = data.get('sections', {})
        
        # Update sections
        for section_name, section_data in updated_sections.items():
            section = ResumeSection.query.filter_by(
                resume_id=file_id,
                section_name=section_name
            ).first()
            
            if section:
                section.section_data = section_data
                section.last_updated = datetime.utcnow()
                section.manually_edited = True
            else:
                # Create new section
                section = ResumeSection(
                    resume_id=file_id,
                    section_name=section_name,
                    section_data=section_data,
                    confidence_score=1.0,  # User edited = high confidence
                    manually_edited=True,
                    last_updated=datetime.utcnow()
                )
                db.session.add(section)
        
        # Update resume metadata
        resume.last_updated = datetime.utcnow()
        if data.get('metadata'):
            resume.metadata = {**(resume.metadata or {}), **data['metadata']}
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resume data updated successfully',
            'updated_at': resume.last_updated.isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Data update error: {str(e)}")
        raise ProcessingError('Failed to update resume data')

@resume_bp.route('/list', methods=['GET'])
@login_required
def list_resumes():
    """
    List user's uploaded resumes
    ---
    tags:
      - Resume Builder
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Filter by status
      - name: limit
        in: query
        type: integer
        default: 20
        description: Number of results to return
      - name: offset
        in: query
        type: integer
        default: 0
        description: Number of results to skip
    responses:
      200:
        description: Resume list retrieved
        schema:
          type: object
          properties:
            resumes:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  filename:
                    type: string
                  status:
                    type: string
                  upload_time:
                    type: string
                    format: date-time
                  file_size:
                    type: integer
                  confidence_score:
                    type: number
            total_count:
              type: integer
            has_more:
              type: boolean
    """
    
    try:
        status_filter = request.args.get('status')
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        
        query = Resume.query.filter_by(user_id=request.current_user.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        total_count = query.count()
        resumes = query.order_by(Resume.upload_time.desc())\
                      .limit(limit)\
                      .offset(offset)\
                      .all()
        
        return jsonify({
            'resumes': [
                {
                    'id': resume.id,
                    'filename': resume.original_filename,
                    'status': resume.status,
                    'upload_time': resume.upload_time.isoformat(),
                    'file_size': resume.file_size,
                    'confidence_score': resume.confidence_score
                }
                for resume in resumes
            ],
            'total_count': total_count,
            'has_more': (offset + len(resumes)) < total_count
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"List error: {str(e)}")
        raise ProcessingError('Failed to list resumes')

@resume_bp.route('/<file_id>', methods=['DELETE'])
@login_required
def delete_resume(file_id):
    """
    Delete resume and associated data
    ---
    tags:
      - Resume Builder
    parameters:
      - name: file_id
        in: path
        type: string
        required: true
        description: Resume file ID
    responses:
      200:
        description: Resume deleted successfully
      404:
        description: Resume not found
    """
    
    try:
        resume = Resume.query.filter_by(
            id=file_id,
            user_id=request.current_user.id
        ).first()
        
        if not resume:
            raise NotFoundError('Resume not found')
        
        # Delete file from storage
        try:
            if os.path.exists(resume.file_path):
                os.remove(resume.file_path)
        except Exception as e:
            current_app.logger.warning(f"Failed to delete file {resume.file_path}: {str(e)}")
        
        # Delete sections
        ResumeSection.query.filter_by(resume_id=file_id).delete()
        
        # Delete extraction jobs
        ExtractionJob.query.filter_by(resume_id=file_id).delete()
        
        # Delete resume record
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({
            'message': 'Resume deleted successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Delete error: {str(e)}")
        raise ProcessingError('Failed to delete resume')

# Error handlers
@resume_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({'error': str(error)}), 400

@resume_bp.errorhandler(ProcessingError)
def handle_processing_error(error):
    return jsonify({'error': str(error)}), 500

@resume_bp.errorhandler(NotFoundError)
def handle_not_found_error(error):
    return jsonify({'error': str(error)}), 404 