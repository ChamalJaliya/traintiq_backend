import os
import uuid
import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.profile import Profile, ProfileDocument, ProfileTemplate, ProfileEmbedding
from app.schemas.profile import (
    ProfileCreateRequest, ProfileResponse, ProfileListResponse,
    ProfileUpdateRequest, ProfileGenerationRequest, ProfileSearchRequest,
    ProfileSearchResponse, BulkProfileGenerationRequest, BulkOperationResponse,
    ProfileTemplateCreate, ProfileTemplateResponse, ProfileAnalytics,
    DocumentUploadResponse, ProfileStatus, FileType
)
from app.services.core.celery_tasks import (
    process_document_task, generate_profile_task,
    bulk_process_documents_task, bulk_generate_profiles_task
)
from app.services.data.document_processor import DocumentProcessor
from app.services.ai.profile_generator import ProfileGenerator
from app.services.data.scraping_service import EnhancedScrapingService
from app.services.data.data_extraction_service import DataExtractionService

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.html'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=ProfileResponse)
async def create_profile(
    profile_data: ProfileCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new profile"""
    try:
        # Validate template if provided
        template = None
        if profile_data.template_id:
            template = db.query(ProfileTemplate).filter(
                ProfileTemplate.id == profile_data.template_id,
                ProfileTemplate.is_active == True
            ).first()
            if not template:
                raise HTTPException(status_code=404, detail="Template not found or inactive")
        
        # Create profile
        profile = Profile(
            title=profile_data.title,
            description=profile_data.description,
            profile_type=profile_data.profile_type.value,
            custom_instructions=profile_data.custom_instructions,
            template_id=profile_data.template_id,
            status=ProfileStatus.PENDING
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Created profile {profile.id}")
        return profile
        
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProfileListResponse])
async def list_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ProfileStatus] = None,
    profile_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List profiles with pagination and filtering"""
    try:
        query = db.query(Profile)
        
        # Apply filters
        if status:
            query = query.filter(Profile.status == status.value)
        if profile_type:
            query = query.filter(Profile.profile_type == profile_type)
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination and get results
        profiles = query.offset(skip).limit(limit).all()
        
        # Add document count to each profile
        results = []
        for profile in profiles:
            document_count = db.query(func.count(ProfileDocument.id)).filter(
                ProfileDocument.profile_id == profile.id
            ).scalar()
            
            profile_data = ProfileListResponse.from_orm(profile)
            profile_data.document_count = document_count
            results.append(profile_data)
        
        return results
        
    except Exception as e:
        logger.error(f"Error listing profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a specific profile by ID"""
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update a profile"""
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Update fields if provided
        if profile_data.title is not None:
            profile.title = profile_data.title
        if profile_data.description is not None:
            profile.description = profile_data.description
        if profile_data.custom_instructions is not None:
            profile.custom_instructions = profile_data.custom_instructions
        if profile_data.template_id is not None:
            # Validate template
            template = db.query(ProfileTemplate).filter(
                ProfileTemplate.id == profile_data.template_id,
                ProfileTemplate.is_active == True
            ).first()
            if not template:
                raise HTTPException(status_code=404, detail="Template not found or inactive")
            profile.template_id = profile_data.template_id
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Updated profile {profile_id}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{profile_id}")
async def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Delete a profile and all associated data"""
    try:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Delete associated files
        documents = db.query(ProfileDocument).filter(ProfileDocument.profile_id == profile_id).all()
        for document in documents:
            try:
                if os.path.exists(document.file_path):
                    os.remove(document.file_path)
            except Exception as e:
                logger.warning(f"Could not delete file {document.file_path}: {str(e)}")
        
        # Delete profile (cascade will handle related records)
        db.delete(profile)
        db.commit()
        
        logger.info(f"Deleted profile {profile_id}")
        return JSONResponse(content={"message": "Profile deleted successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{profile_id}/documents", response_model=List[DocumentUploadResponse])
async def upload_documents(
    profile_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload documents for a profile"""
    try:
        # Verify profile exists
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        uploaded_documents = []
        
        for file in files:
            # Validate file
            if not file.filename:
                continue
            
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB"
                )
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            safe_filename = f"{file_id}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Create document record
            document = ProfileDocument(
                profile_id=profile_id,
                original_filename=file.filename,
                file_path=file_path,
                file_type=file_extension[1:],  # Remove the dot
                file_size=len(file_content)
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Queue document processing
            process_document_task.delay(document.id)
            
            uploaded_documents.append(
                DocumentUploadResponse(
                    id=document.id,
                    filename=document.original_filename,
                    file_type=FileType(document.file_type),
                    file_size=document.file_size,
                    uploaded_at=document.uploaded_at
                )
            )
        
        logger.info(f"Uploaded {len(uploaded_documents)} documents for profile {profile_id}")
        return uploaded_documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents for profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{profile_id}/documents")
async def get_profile_documents(profile_id: int, db: Session = Depends(get_db)):
    """Get all documents for a profile"""
    try:
        # Verify profile exists
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        documents = db.query(ProfileDocument).filter(ProfileDocument.profile_id == profile_id).all()
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents for profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{profile_id}/generate")
async def generate_profile(
    profile_id: int,
    generation_request: ProfileGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate profile content from uploaded documents"""
    try:
        # Verify profile exists
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Check if profile has processed documents
        processed_docs = db.query(ProfileDocument).filter(
            ProfileDocument.profile_id == profile_id,
            ProfileDocument.processed == True
        ).count()
        
        if processed_docs == 0:
            raise HTTPException(
                status_code=400,
                detail="No processed documents found. Please upload and wait for document processing to complete."
            )
        
        # Queue profile generation
        task = generate_profile_task.delay(profile_id, generation_request.force_regenerate)
        
        return JSONResponse(content={
            "message": "Profile generation started",
            "task_id": task.id,
            "profile_id": profile_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting profile generation for {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=ProfileSearchResponse)
async def search_profiles(
    search_request: ProfileSearchRequest,
    db: Session = Depends(get_db)
):
    """Search profiles using semantic similarity"""
    try:
        # Initialize document processor for embeddings
        processor = DocumentProcessor()
        
        # Generate query embedding
        query_embedding = processor.generate_embeddings(search_request.query)
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Could not generate query embedding")
        
        # This is a simplified similarity search
        # In production, you'd use a proper vector database like Pinecone or Weaviate
        
        # Get all profile embeddings
        embeddings = db.query(ProfileEmbedding).filter(
            ProfileEmbedding.content_type == 'full_profile'
        ).all()
        
        # Calculate similarities (simplified cosine similarity)
        def cosine_similarity(a, b):
            import numpy as np
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        results = []
        for embedding in embeddings:
            try:
                similarity = cosine_similarity(query_embedding, embedding.embedding_vector)
                if similarity >= search_request.similarity_threshold:
                    profile = db.query(Profile).filter(Profile.id == embedding.profile_id).first()
                    if profile:
                        results.append({
                            'profile': profile,
                            'similarity': float(similarity)
                        })
            except Exception as e:
                logger.warning(f"Error calculating similarity for embedding {embedding.id}: {str(e)}")
                continue
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        results = results[:search_request.limit]
        
        # Format response
        search_results = []
        for result in results:
            search_results.append({
                'id': result['profile'].id,
                'title': result['profile'].title,
                'description': result['profile'].description,
                'profile_type': result['profile'].profile_type,
                'similarity_score': result['similarity'],
                'generated_at': result['profile'].generated_at
            })
        
        return ProfileSearchResponse(
            results=search_results,
            total_count=len(search_results),
            query=search_request.query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk/generate", response_model=BulkOperationResponse)
async def bulk_generate_profiles(
    bulk_request: BulkProfileGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate multiple profiles in bulk"""
    try:
        # Validate all profiles exist
        existing_profiles = db.query(Profile).filter(
            Profile.id.in_(bulk_request.profile_ids)
        ).count()
        
        if existing_profiles != len(bulk_request.profile_ids):
            raise HTTPException(status_code=400, detail="Some profiles not found")
        
        # Queue bulk generation
        task = bulk_generate_profiles_task.delay(
            bulk_request.profile_ids,
            bulk_request.force_regenerate
        )
        
        return BulkOperationResponse(
            success_count=0,  # Will be updated when task completes
            failed_count=0,
            task_ids=[task.id],
            message=f"Bulk generation started for {len(bulk_request.profile_ids)} profiles"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk profile generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics", response_model=ProfileAnalytics)
async def get_profile_analytics(db: Session = Depends(get_db)):
    """Get analytics about profiles"""
    try:
        total_profiles = db.query(Profile).count()
        
        # Profiles by status
        status_counts = db.query(
            Profile.status, func.count(Profile.id)
        ).group_by(Profile.status).all()
        
        profiles_by_status = {status: count for status, count in status_counts}
        
        # Profiles by type
        type_counts = db.query(
            Profile.profile_type, func.count(Profile.id)
        ).group_by(Profile.profile_type).all()
        
        profiles_by_type = {ptype: count for ptype, count in type_counts}
        
        # Average confidence score
        avg_confidence = db.query(func.avg(Profile.confidence_score)).filter(
            Profile.confidence_score.isnot(None)
        ).scalar()
        
        # Success rate
        completed_profiles = db.query(Profile).filter(
            Profile.status == ProfileStatus.COMPLETED
        ).count()
        
        success_rate = (completed_profiles / total_profiles * 100) if total_profiles > 0 else 0
        
        return ProfileAnalytics(
            total_profiles=total_profiles,
            profiles_by_status=profiles_by_status,
            profiles_by_type=profiles_by_type,
            average_confidence_score=float(avg_confidence) if avg_confidence else None,
            processing_success_rate=success_rate
        )
        
    except Exception as e:
        logger.error(f"Error getting profile analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Template management endpoints
@router.post("/templates", response_model=ProfileTemplateResponse)
async def create_template(
    template_data: ProfileTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new profile template"""
    try:
        template = ProfileTemplate(
            name=template_data.name,
            description=template_data.description,
            template_type=template_data.template_type.value,
            prompt_template=template_data.prompt_template,
            system_instructions=template_data.system_instructions,
            is_active=template_data.is_active,
            is_default=template_data.is_default,
            configuration=template_data.configuration
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        logger.info(f"Created template {template.id}")
        return template
        
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=List[ProfileTemplateResponse])
async def list_templates(
    active_only: bool = Query(True),
    template_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List profile templates"""
    try:
        query = db.query(ProfileTemplate)
        
        if active_only:
            query = query.filter(ProfileTemplate.is_active == True)
        if template_type:
            query = query.filter(ProfileTemplate.template_type == template_type)
        
        templates = query.all()
        return templates
        
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-enhanced", response_model=Dict[str, Any])
async def generate_enhanced_profile(
    urls: List[str] = Form(...),
    custom_instructions: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Enhanced company profile generation from multiple URLs and documents"""
    try:
        # Initialize services
        scraping_service = EnhancedScrapingService()
        document_processor = DocumentProcessor()
        data_extraction_service = DataExtractionService()
        profile_generator = ProfileGenerator()
        
        # Results container
        generation_results = {
            'status': 'processing',
            'scraped_data': {},
            'processed_documents': [],
            'extracted_company_data': {},
            'generated_profile': None,
            'errors': [],
            'metadata': {}
        }
        
        # Step 1: Scrape multiple URLs concurrently
        if urls:
            logger.info(f"Starting to scrape {len(urls)} URLs")
            try:
                scraping_results = await scraping_service.scrape_multiple_urls(urls, custom_instructions)
                generation_results['scraped_data'] = scraping_results['scraped_data']
                generation_results['metadata']['scraping'] = {
                    'successful_urls': len(scraping_results['scraped_data']),
                    'failed_urls': len(scraping_results['failed_urls']),
                    'summary': scraping_results['summary']
                }
                
                if scraping_results['failed_urls']:
                    generation_results['errors'].extend([
                        f"Failed to scrape {fail['url']}: {fail['error']}" 
                        for fail in scraping_results['failed_urls']
                    ])
                    
            except Exception as e:
                logger.error(f"URL scraping failed: {e}")
                generation_results['errors'].append(f"URL scraping error: {str(e)}")
        
        # Step 2: Process uploaded documents
        document_contents = []
        if files and len(files) > 0:
            logger.info(f"Processing {len(files)} uploaded documents")
            for file in files:
                if file.filename and file.size > 0:
                    try:
                        # Save file temporarily
                        file_path = os.path.join(UPLOAD_DIR, f"temp_{uuid.uuid4()}_{file.filename}")
                        with open(file_path, "wb") as buffer:
                            content = await file.read()
                            buffer.write(content)
                        
                        # Extract text from file
                        file_extension = os.path.splitext(file.filename)[1].lower()
                        if file_extension in ['.pdf', '.docx', '.txt', '.html']:
                            text_content, extraction_metadata = document_processor.extract_text_from_file(
                                file_path, file_extension[1:]  # Remove the dot
                            )
                            
                            if text_content:
                                document_contents.append(text_content)
                                generation_results['processed_documents'].append({
                                    'filename': file.filename,
                                    'status': 'success',
                                    'text_length': len(text_content),
                                    'metadata': extraction_metadata
                                })
                            else:
                                generation_results['processed_documents'].append({
                                    'filename': file.filename,
                                    'status': 'failed',
                                    'error': 'No text content extracted'
                                })
                        
                        # Clean up temporary file
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            
                    except Exception as e:
                        logger.error(f"Document processing failed for {file.filename}: {e}")
                        generation_results['errors'].append(f"Document processing error for {file.filename}: {str(e)}")
                        generation_results['processed_documents'].append({
                            'filename': file.filename,
                            'status': 'failed',
                            'error': str(e)
                        })
        
        # Step 3: Extract structured company data from scraped content
        all_scraped_text = []
        if generation_results['scraped_data']:
            for url, scraped_content in generation_results['scraped_data'].items():
                if isinstance(scraped_content, dict) and 'raw_text' in scraped_content:
                    all_scraped_text.append(scraped_content['raw_text'])
                    
                    # Extract structured company data using data extraction service
                    try:
                        company_data = data_extraction_service.extract_company_data(
                            scraped_content['raw_text'], 
                            custom_instructions,
                            [url]
                        )
                        generation_results['extracted_company_data'][url] = company_data
                    except Exception as e:
                        logger.error(f"Data extraction failed for {url}: {e}")
                        generation_results['errors'].append(f"Data extraction error for {url}: {str(e)}")
        
        # Step 4: Combine all content for profile generation
        all_content = all_scraped_text + document_contents
        
        if not all_content:
            raise HTTPException(status_code=400, detail="No content available for profile generation")
        
        # Step 5: Generate comprehensive company profile using AI
        try:
            logger.info("Generating AI-powered company profile")
            generated_profile, profile_metadata = await profile_generator.generate_profile(
                all_content,
                profile_type='company_comprehensive',
                custom_instructions=custom_instructions
            )
            
            generation_results['generated_profile'] = generated_profile
            generation_results['metadata']['profile_generation'] = profile_metadata
            generation_results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Profile generation failed: {e}")
            generation_results['errors'].append(f"AI profile generation error: {str(e)}")
            generation_results['status'] = 'failed'
        
        # Step 6: Save to database if successful
        if generation_results['status'] == 'completed':
            try:
                # Create profile record
                profile = Profile(
                    title=f"Enhanced Profile - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    description=f"Generated from {len(urls)} URLs and {len(files)} documents",
                    profile_type='company_comprehensive',
                    custom_instructions=custom_instructions,
                    content=generated_profile,
                    metadata=json.dumps(generation_results['metadata']),
                    status=ProfileStatus.COMPLETED
                )
                
                db.add(profile)
                db.commit()
                db.refresh(profile)
                
                generation_results['profile_id'] = profile.id
                logger.info(f"Saved enhanced profile with ID: {profile.id}")
                
            except Exception as e:
                logger.error(f"Database save failed: {e}")
                generation_results['errors'].append(f"Database save error: {str(e)}")
        
        return generation_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced profile generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Profile generation failed: {str(e)}") 