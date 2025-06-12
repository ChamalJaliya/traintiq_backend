import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from celery import Celery
from sqlalchemy.orm import Session

from app import db
from app.models.profile import Profile, ProfileDocument, ProfileEmbedding
from app.services.data.document_processor import DocumentProcessor
from app.services.ai.profile_generator import ProfileGenerator
from app.schemas.profile import ProfileStatus

# Initialize Celery
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('profile_generator', broker=redis_url, backend=redis_url)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='process_document')
def process_document_task(self, document_id: int) -> Dict[str, Any]:
    """
    Process a single document: extract text and analyze content
    
    Args:
        document_id: ID of the document to process
        
    Returns:
        Dictionary with processing results
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Starting document processing'})
        
        # Use db.session directly
        document = db.session.query(ProfileDocument).filter(ProfileDocument.id == document_id).first()
        
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Extracting text from document'})
        
        # Extract text from file
        extracted_text, extraction_metadata = processor.extract_text_from_file(
            document.file_path,
            document.file_type
        )
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Analyzing document content'})
        
        # Analyze content
        content_analysis = processor.analyze_content(extracted_text)
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Generating embeddings'})
        
        # Generate embeddings
        embeddings = processor.generate_embeddings(extracted_text)
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Saving results to database'})
        
        # Update document in database
        document.extracted_content = extracted_text
        document.extraction_metadata = {
            'extraction_metadata': extraction_metadata,
            'content_analysis': content_analysis
        }
        document.processed = True
        document.processed_at = datetime.utcnow()
        
        # Create embedding record if embeddings were generated
        if embeddings:
            content_hash = processor.calculate_content_hash(extracted_text)
            
            embedding_record = ProfileEmbedding(
                profile_id=document.profile_id,
                embedding_vector=embeddings,
                embedding_model='all-MiniLM-L6-v2',
                content_type='document',
                content_hash=content_hash
            )
            db.session.add(embedding_record)
        
        db.session.commit()
        
        result = {
            'document_id': document_id,
            'status': 'completed',
            'extracted_text_length': len(extracted_text),
            'extraction_metadata': extraction_metadata,
            'content_analysis': content_analysis,
            'has_embeddings': embeddings is not None
        }
        
        logger.info(f"Successfully processed document {document_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update document status in database
        try:
            document = db.session.query(ProfileDocument).filter(ProfileDocument.id == document_id).first()
            if document:
                document.extraction_metadata = {'error': str(e)}
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Error updating document status: {str(db_error)}")
        
        # Re-raise the exception for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='generate_profile')
def generate_profile_task(self, profile_id: int, force_regenerate: bool = False) -> Dict[str, Any]:
    """
    Generate a profile from processed documents
    
    Args:
        profile_id: ID of the profile to generate
        force_regenerate: Whether to regenerate even if already exists
        
    Returns:
        Dictionary with generation results
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Starting profile generation'})
        
        profile = db.session.query(Profile).filter(Profile.id == profile_id).first()
        
        if not profile:
            raise ValueError(f"Profile with ID {profile_id} not found")
        
        # Check if regeneration is needed
        if profile.status == ProfileStatus.COMPLETED and not force_regenerate:
            return {
                'profile_id': profile_id,
                'status': 'skipped',
                'message': 'Profile already generated and force_regenerate is False'
            }
        
        # Update profile status
        profile.status = ProfileStatus.PROCESSING
        db.session.commit()
        
        # Get processed documents
        documents = db.session.query(ProfileDocument).filter(
            ProfileDocument.profile_id == profile_id,
            ProfileDocument.processed == True
        ).all()
        
        if not documents:
            raise ValueError(f"No processed documents found for profile {profile_id}")
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Extracting content from documents'})
        
        # Extract content from all documents
        documents_content = []
        for doc in documents:
            if doc.extracted_content:
                documents_content.append(doc.extracted_content)
        
        if not documents_content:
            raise ValueError(f"No extracted content found for profile {profile_id}")
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Initializing AI generator'})
        
        # Initialize profile generator
        generator = ProfileGenerator()
        
        # Get template if specified
        template = None
        if profile.template:
            template = {
                'name': profile.template.name,
                'prompt_template': profile.template.prompt_template,
                'system_instructions': profile.template.system_instructions,
                'configuration': profile.template.configuration
            }
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Generating profile content'})
        
        # Generate profile (remove await since Celery tasks are not async)
        generated_content, generation_metadata = generator.generate_profile(
            documents_content=documents_content,
            profile_type=profile.profile_type,
            custom_instructions=profile.custom_instructions,
            template=template
        )
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Creating profile embeddings'})
        
        # Generate embeddings for the profile
        processor = DocumentProcessor()
        profile_embeddings = processor.generate_embeddings(generated_content)
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Saving profile to database'})
        
        # Update profile in database
        profile.content = generated_content
        profile.status = ProfileStatus.COMPLETED
        profile.processing_metadata = generation_metadata
        profile.confidence_score = generation_metadata.get('confidence_score', 0.0)
        profile.updated_at = datetime.utcnow()
        
        # Create profile embedding record
        if profile_embeddings:
            content_hash = processor.calculate_content_hash(generated_content)
            
            # Remove existing embeddings for this profile
            db.session.query(ProfileEmbedding).filter(
                ProfileEmbedding.profile_id == profile_id,
                ProfileEmbedding.content_type == 'full_profile'
            ).delete()
            
            embedding_record = ProfileEmbedding(
                profile_id=profile_id,
                embedding_vector=profile_embeddings,
                embedding_model='all-MiniLM-L6-v2',
                content_type='full_profile',
                content_hash=content_hash
            )
            db.session.add(embedding_record)
        
        db.session.commit()
        
        result = {
            'profile_id': profile_id,
            'status': 'completed',
            'generated_content_length': len(generated_content),
            'confidence_score': generation_metadata.get('confidence_score', 0.0),
            'generation_metadata': generation_metadata,
            'documents_processed': len(documents_content)
        }
        
        logger.info(f"Successfully generated profile {profile_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating profile {profile_id}: {str(e)}")
        
        # Update profile status in database
        try:
            profile = db.session.query(Profile).filter(Profile.id == profile_id).first()
            if profile:
                profile.status = ProfileStatus.FAILED
                profile.processing_metadata = {'error': str(e), 'failed_at': datetime.utcnow().isoformat()}
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Error updating profile status: {str(db_error)}")
        
        # Re-raise the exception for Celery to handle
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='bulk_process_documents')
def bulk_process_documents_task(self, document_ids: List[int]) -> Dict[str, Any]:
    """
    Process multiple documents in parallel
    
    Args:
        document_ids: List of document IDs to process
        
    Returns:
        Dictionary with bulk processing results
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Starting bulk document processing'})
        
        results = []
        failed_documents = []
        
        for i, doc_id in enumerate(document_ids):
            try:
                # Update progress
                progress = (i + 1) / len(document_ids) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'stage': f'Processing document {i + 1} of {len(document_ids)}',
                        'progress': progress
                    }
                )
                
                # Process individual document
                result = process_document_task.apply(args=[doc_id])
                results.append(result.get())
                
            except Exception as e:
                logger.error(f"Error processing document {doc_id} in bulk operation: {str(e)}")
                failed_documents.append({'document_id': doc_id, 'error': str(e)})
        
        return {
            'status': 'completed',
            'total_documents': len(document_ids),
            'successful_documents': len(results),
            'failed_documents': len(failed_documents),
            'results': results,
            'failures': failed_documents
        }
        
    except Exception as e:
        logger.error(f"Error in bulk document processing: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(bind=True, name='bulk_generate_profiles')
def bulk_generate_profiles_task(self, profile_ids: List[int], force_regenerate: bool = False) -> Dict[str, Any]:
    """
    Generate multiple profiles in parallel
    
    Args:
        profile_ids: List of profile IDs to generate
        force_regenerate: Whether to regenerate existing profiles
        
    Returns:
        Dictionary with bulk generation results
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'stage': 'Starting bulk profile generation'})
        
        results = []
        failed_profiles = []
        
        for i, profile_id in enumerate(profile_ids):
            try:
                # Update progress
                progress = (i + 1) / len(profile_ids) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'stage': f'Generating profile {i + 1} of {len(profile_ids)}',
                        'progress': progress
                    }
                )
                
                # Generate individual profile
                result = generate_profile_task.apply(args=[profile_id, force_regenerate])
                results.append(result.get())
                
            except Exception as e:
                logger.error(f"Error generating profile {profile_id} in bulk operation: {str(e)}")
                failed_profiles.append({'profile_id': profile_id, 'error': str(e)})
        
        return {
            'status': 'completed',
            'total_profiles': len(profile_ids),
            'successful_profiles': len(results),
            'failed_profiles': len(failed_profiles),
            'results': results,
            'failures': failed_profiles
        }
        
    except Exception as e:
        logger.error(f"Error in bulk profile generation: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(name='update_embeddings')
def update_embeddings_task(profile_id: int) -> Dict[str, Any]:
    """
    Update embeddings for a profile (useful when embedding model changes)
    
    Args:
        profile_id: ID of the profile to update embeddings for
        
    Returns:
        Dictionary with update results
    """
    try:
        profile = db.session.query(Profile).filter(Profile.id == profile_id).first()
        
        if not profile:
            raise ValueError(f"Profile with ID {profile_id} not found")
        
        if not profile.content:
            raise ValueError(f"Profile {profile_id} has no content to generate embeddings for")
        
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Generate new embeddings
        new_embeddings = processor.generate_embeddings(profile.content)
        
        if new_embeddings:
            content_hash = processor.calculate_content_hash(profile.content)
            
            # Remove existing embeddings
            db.session.query(ProfileEmbedding).filter(
                ProfileEmbedding.profile_id == profile_id,
                ProfileEmbedding.content_type == 'full_profile'
            ).delete()
            
            # Create new embedding record
            embedding_record = ProfileEmbedding(
                profile_id=profile_id,
                embedding_vector=new_embeddings,
                embedding_model='all-MiniLM-L6-v2',
                content_type='full_profile',
                content_hash=content_hash
            )
            db.session.add(embedding_record)
            db.session.commit()
            
            return {
                'profile_id': profile_id,
                'status': 'completed',
                'embeddings_updated': True,
                'embedding_model': 'all-MiniLM-L6-v2'
            }
        else:
            return {
                'profile_id': profile_id,
                'status': 'failed',
                'embeddings_updated': False,
                'error': 'Failed to generate embeddings'
            }
            
    except Exception as e:
        logger.error(f"Error updating embeddings for profile {profile_id}: {str(e)}")
        return {
            'profile_id': profile_id,
            'status': 'failed',
            'embeddings_updated': False,
            'error': str(e)
        }

@celery_app.task(name='health_check')
def health_check_task() -> Dict[str, Any]:
    """Health check task for monitoring Celery workers"""
    try:
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'worker_id': os.getpid()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@celery_app.task(name='cleanup_old_tasks')
def cleanup_old_tasks() -> Dict[str, Any]:
    """Clean up old task results and logs"""
    try:
        # This would typically clean up old Celery results
        # Implementation depends on your specific cleanup requirements
        return {
            'status': 'completed',
            'cleaned_tasks': 0,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        } 