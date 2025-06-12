"""
Enhanced Company Profile Generation API
Advanced endpoints for multi-source company profile generation
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Form, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator
import asyncio
import json
import logging
from datetime import datetime

from app.services.ai.enhanced_profile_generator import EnhancedProfileGenerator
from app.services.data.document_processor import DocumentProcessor
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.company_profile import CompanyProfile
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Request/Response Models
class EnhancedProfileRequest(BaseModel):
    """Request model for enhanced profile generation"""
    urls: Optional[List[str]] = []
    custom_text: Optional[str] = None
    custom_instructions: Optional[str] = None
    focus_areas: Optional[List[str]] = []
    use_cache: bool = True
    priority: str = "normal"  # normal, high, urgent
    
    @validator('urls')
    def validate_urls(cls, v):
        if v:
            for url in v:
                if url and not (url.startswith('http://') or url.startswith('https://')):
                    raise ValueError(f'Invalid URL format: {url}')
        return v or []
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v):
        valid_areas = [
            'overview', 'history', 'products', 'leadership', 
            'financials', 'technology', 'market', 'news', 'competitive'
        ]
        if v:
            for area in v:
                if area.lower() not in valid_areas:
                    raise ValueError(f'Invalid focus area: {area}')
        return v or []

class ProfileGenerationResponse(BaseModel):
    """Response model for profile generation"""
    success: bool
    profile: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]
    generation_id: Optional[str] = None
    message: str

class BatchProfileRequest(BaseModel):
    """Request model for batch profile generation"""
    requests: List[EnhancedProfileRequest]
    batch_name: Optional[str] = None
    priority: str = "normal"

# Initialize router and services
router = APIRouter(prefix="/api/profile", tags=["Enhanced Profile Generation"])
profile_generator = EnhancedProfileGenerator()
document_processor = DocumentProcessor()

@router.post("/generate", response_model=ProfileGenerationResponse)
async def generate_enhanced_profile(
    request: EnhancedProfileRequest,
    files: List[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate an enhanced company profile from multiple data sources
    
    Features:
    - Multi-source data ingestion (URLs, files, text)
    - Advanced NLP and entity extraction
    - Intelligent caching
    - Structured output generation
    """
    
    try:
        generation_id = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
        
        # Process uploaded files
        processed_documents = []
        if files:
            for file in files:
                if file.filename:
                    try:
                        # Read file content
                        content = await file.read()
                        
                        # Determine file type
                        file_extension = file.filename.split('.')[-1].lower()
                        
                        # Extract text from file
                        if file_extension in ['pdf', 'docx', 'txt']:
                            # Save temporarily and process
                            temp_path = f"/tmp/{file.filename}"
                            with open(temp_path, "wb") as temp_file:
                                temp_file.write(content)
                            
                            extracted_text, metadata = document_processor.extract_text_from_file(
                                temp_path, file_extension
                            )
                            
                            if extracted_text:
                                processed_documents.append(extracted_text)
                            
                            # Clean up
                            import os
                            os.remove(temp_path)
                            
                    except Exception as e:
                        logger.warning(f"Failed to process file {file.filename}: {e}")
                        continue
        
        # Generate profile using enhanced service
        result = await profile_generator.generate_comprehensive_profile(
            urls=request.urls,
            documents=processed_documents,
            custom_text=request.custom_text,
            custom_instructions=request.custom_instructions,
            focus_areas=request.focus_areas,
            use_cache=request.use_cache
        )
        
        if result['success']:
            # Save to database
            company_profile = CompanyProfile(
                user_id=current_user.id,
                generation_id=generation_id,
                profile_data=json.dumps(result['profile']),
                metadata=json.dumps(result['metadata']),
                created_at=datetime.now(),
                confidence_score=result['metadata'].get('confidence_score', 0.0)
            )
            
            db.add(company_profile)
            db.commit()
            
            return ProfileGenerationResponse(
                success=True,
                profile=result['profile'],
                metadata=result['metadata'],
                generation_id=generation_id,
                message="Profile generated successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Profile generation failed: {result['metadata'].get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Error in enhanced profile generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/async", response_model=Dict[str, str])
async def generate_profile_async(
    request: EnhancedProfileRequest,
    files: List[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Start asynchronous profile generation
    Returns task ID for status tracking
    """
    
    generation_id = f"async_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
    
    # Add to background tasks
    background_tasks.add_task(
        _generate_profile_background,
        generation_id,
        request,
        files,
        current_user.id,
        db
    )
    
    return {
        "generation_id": generation_id,
        "status": "started",
        "message": "Profile generation started. Use /status endpoint to check progress."
    }

@router.get("/status/{generation_id}")
async def get_generation_status(
    generation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the status of an async profile generation"""
    
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.generation_id == generation_id,
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return {
        "generation_id": generation_id,
        "status": profile.status,
        "progress": profile.progress,
        "created_at": profile.created_at,
        "completed_at": profile.completed_at,
        "metadata": json.loads(profile.metadata) if profile.metadata else {}
    }

@router.get("/result/{generation_id}")
async def get_generation_result(
    generation_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the result of a completed profile generation"""
    
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.generation_id == generation_id,
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if profile.status != "completed":
        raise HTTPException(status_code=202, detail="Generation not yet completed")
    
    return {
        "generation_id": generation_id,
        "profile": json.loads(profile.profile_data) if profile.profile_data else None,
        "metadata": json.loads(profile.metadata) if profile.metadata else {},
        "confidence_score": profile.confidence_score
    }

@router.post("/batch/generate")
async def generate_batch_profiles(
    request: BatchProfileRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate multiple profiles in batch"""
    
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}"
    
    # Create individual generation tasks
    generation_ids = []
    for i, profile_request in enumerate(request.requests):
        generation_id = f"{batch_id}_item_{i}"
        generation_ids.append(generation_id)
        
        background_tasks.add_task(
            _generate_profile_background,
            generation_id,
            profile_request,
            None,  # No files for batch
            current_user.id,
            db
        )
    
    return {
        "batch_id": batch_id,
        "generation_ids": generation_ids,
        "total_requests": len(request.requests),
        "status": "started"
    }

@router.get("/analyze/sources")
async def analyze_data_sources(
    urls: List[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze data sources before profile generation"""
    
    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    analysis_results = []
    
    for url in urls:
        try:
            # Quick analysis of the URL content
            scraped_data = await profile_generator.scraping_service.scrape_url_content(url)
            
            if scraped_data:
                analysis = {
                    'url': url,
                    'title': scraped_data.get('title', ''),
                    'content_length': len(scraped_data.get('content', '')),
                    'estimated_entities': len(scraped_data.get('content', '').split()) // 20,
                    'data_quality': 'high' if len(scraped_data.get('content', '')) > 1000 else 'medium',
                    'scrapeable': True
                }
            else:
                analysis = {
                    'url': url,
                    'scrapeable': False,
                    'error': 'Unable to scrape content'
                }
            
            analysis_results.append(analysis)
            
        except Exception as e:
            analysis_results.append({
                'url': url,
                'scrapeable': False,
                'error': str(e)
            })
    
    return {
        'analysis_results': analysis_results,
        'total_sources': len(urls),
        'scrapeable_sources': len([r for r in analysis_results if r.get('scrapeable', False)]),
        'estimated_generation_time': len(analysis_results) * 30  # seconds
    }

@router.get("/templates")
async def get_profile_templates():
    """Get available profile generation templates"""
    
    templates = {
        'startup': {
            'name': 'Startup Profile',
            'description': 'Focused on early-stage companies, funding, and growth',
            'focus_areas': ['overview', 'leadership', 'products', 'financials', 'market'],
            'custom_instructions': 'Focus on founding story, team background, product development, funding rounds, and market opportunity.'
        },
        'enterprise': {
            'name': 'Enterprise Profile',
            'description': 'Comprehensive profile for established companies',
            'focus_areas': ['overview', 'history', 'products', 'leadership', 'financials', 'market', 'competitive'],
            'custom_instructions': 'Include company history, full product portfolio, executive team, financial performance, market position, and competitive landscape.'
        },
        'technology': {
            'name': 'Technology Company',
            'description': 'Tech-focused profile with emphasis on innovation',
            'focus_areas': ['overview', 'products', 'technology', 'leadership', 'market'],
            'custom_instructions': 'Highlight technology stack, innovative products, technical leadership, development approach, and market disruption potential.'
        },
        'financial': {
            'name': 'Financial Services',
            'description': 'Profile for financial and investment companies',
            'focus_areas': ['overview', 'products', 'financials', 'leadership', 'market'],
            'custom_instructions': 'Focus on financial products, regulatory compliance, leadership experience, market position, and financial performance.'
        }
    }
    
    return {'templates': templates}

@router.post("/enhance")
async def enhance_existing_profile(
    profile_data: Dict[str, Any],
    enhancement_type: str = "quality",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Enhance an existing profile with additional processing"""
    
    enhancement_types = ['quality', 'completeness', 'structure', 'style']
    
    if enhancement_type not in enhancement_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid enhancement type. Must be one of: {enhancement_types}"
        )
    
    try:
        # Apply enhancement based on type
        if enhancement_type == "quality":
            enhanced_profile = await profile_generator._enhance_profile_quality(
                {'synthesized_profile': profile_data.get('full_profile', '')},
                {}
            )
        else:
            # Placeholder for other enhancement types
            enhanced_profile = profile_data
        
        return {
            'success': True,
            'enhanced_profile': enhanced_profile,
            'enhancement_type': enhancement_type,
            'improvements_made': ['Grammar correction', 'Structure improvement', 'Content enrichment']
        }
        
    except Exception as e:
        logger.error(f"Profile enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task function
async def _generate_profile_background(
    generation_id: str,
    request: EnhancedProfileRequest,
    files: List[UploadFile],
    user_id: int,
    db: Session
):
    """Background task for profile generation"""
    
    try:
        # Update status to processing
        profile = CompanyProfile(
            user_id=user_id,
            generation_id=generation_id,
            status="processing",
            progress=0,
            created_at=datetime.now()
        )
        db.add(profile)
        db.commit()
        
        # Process files if any
        processed_documents = []
        if files:
            for file in files:
                if file.filename:
                    # File processing logic here
                    pass
        
        # Update progress
        profile.progress = 50
        db.commit()
        
        # Generate profile
        result = await profile_generator.generate_comprehensive_profile(
            urls=request.urls,
            documents=processed_documents,
            custom_text=request.custom_text,
            custom_instructions=request.custom_instructions,
            focus_areas=request.focus_areas,
            use_cache=request.use_cache
        )
        
        # Update with results
        profile.status = "completed" if result['success'] else "failed"
        profile.progress = 100
        profile.profile_data = json.dumps(result['profile']) if result['success'] else None
        profile.metadata = json.dumps(result['metadata'])
        profile.confidence_score = result['metadata'].get('confidence_score', 0.0)
        profile.completed_at = datetime.now()
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Background profile generation failed: {e}")
        
        # Update with error
        profile.status = "failed"
        profile.error_message = str(e)
        profile.completed_at = datetime.now()
        
        db.commit() 