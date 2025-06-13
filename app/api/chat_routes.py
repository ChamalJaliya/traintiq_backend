"""
Enhanced Chat Routes for TraintiQ
Uses improved architecture with proper logging and service management
"""

from flask import Blueprint, request, jsonify
from app.services.ai.chat_service import ChatService
from app.models.chat import ChatConversation, ChatMessage, ChatAnalytics
from app.core.decorators import (
    with_request_id, validate_request_data, 
    log_execution_time, rate_limit
)
from app.core.base_service import service_registry
from app.core.logger import logger_service
from app import db
import uuid
import time
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
import asyncio
import logging

# Create blueprint with proper logging
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
logger = logging.getLogger(__name__)

# Initialize and register chat service
chat_service = ChatService()
service_registry.register_service(chat_service, 'chat_service')

@chat_bp.route('/health', methods=['GET'])
def chat_health():
    """Health check endpoint with detailed service status"""
    try:
        # Check service status
        service_status = {
            'chat_service': 'healthy',
            'database': 'healthy',
            'openai_api': 'unknown'
        }
        
        # Check database connection
        try:
            db.session.execute('SELECT 1')
            service_status['database'] = 'healthy'
        except Exception:
            service_status['database'] = 'unhealthy'
        
        # Check OpenAI API if available
        try:
            if chat_service.validate_api_key():
                service_status['openai_api'] = 'healthy'
            else:
                service_status['openai_api'] = 'unavailable'
        except:
            service_status['openai_api'] = 'unavailable'
        
        # Overall health
        overall_healthy = all(
            status in ['healthy', 'unknown', 'unavailable'] 
            for status in service_status.values()
        )
        
        logger_service.info("Health check performed", **service_status)
        
        return jsonify({
            'success': True,
            'status': 'healthy' if overall_healthy else 'degraded',
            'services': service_status,
            'timestamp': datetime.now().isoformat(),
            'openai_configured': service_status['openai_api'] == 'healthy'
        }), 200
        
    except Exception as e:
        logger_service.error("Health check failed", error=str(e))
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@chat_bp.route('/message', methods=['POST', 'OPTIONS'])
def chat_message():
    """Send a message to the AI assistant with enhanced logging and error handling"""
    
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        return '', 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
    
    start_time = time.time()
    session_id = None
    conversation = None
    
    try:
        # Validate and extract request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            logger_service.warning("Chat request missing message field")
            return jsonify({
                'success': False,
                'error': 'Message is required',
                'response': 'Please provide a message to continue our conversation.'
            }), 400
        
        message = data['message'].strip()
        if not message:
            logger_service.warning("Chat request with empty message")
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty',
                'response': 'Please enter a message to start our conversation.'
            }), 400
        
        session_id = data.get('session_id', str(uuid.uuid4()))
        conversation_history = data.get('conversation_history', [])
        
        logger_service.info("Processing chat message", 
                          session_id=session_id,
                          message_length=len(message),
                          has_history=bool(conversation_history))
        
        # Get user information
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Find or create conversation
        conversation = get_or_create_conversation(session_id, user_ip, user_agent)
        
        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            message_type='user',
            content=message
        )
        db.session.add(user_message)
        
        # Get conversation history if not provided
        if not conversation_history:
            conversation_history = get_conversation_history(conversation.id)
        
        # Get AI response
        ai_result = get_ai_response_sync(message, conversation_history)
        
        response_time = time.time() - start_time
        
        # Process and save response
        return process_ai_response(ai_result, conversation, session_id, response_time)
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logger_service.error("Database error in chat endpoint", 
                           session_id=session_id,
                           error=str(e))
        return get_error_response(session_id, "Database error occurred")
    
    except Exception as e:
        db.session.rollback()
        logger_service.error("Unexpected error in chat endpoint",
                           session_id=session_id,
                           error=str(e))
        return get_error_response(session_id, "An unexpected error occurred")

@chat_bp.route('/starters', methods=['GET'])
def conversation_starters():
    """Get conversation starters"""
    try:
        # Ensure chat service is initialized
        if not chat_service.prompt_engine:
            chat_service.initialize()
        
        starters = chat_service.get_conversation_starters()
        
        logger_service.trace("Conversation starters retrieved", count=len(starters))
        
        return jsonify({
            'success': True,
            'starters': starters
        }), 200
        
    except Exception as e:
        logger_service.error("Error retrieving conversation starters", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversation starters'
        }), 500

@chat_bp.route('/conversation/<string:session_id>', methods=['GET'])
def get_conversation_history_route(session_id):
    """Get conversation history for a session"""
    try:
        logger_service.info("Retrieving conversation history", session_id=session_id)
        
        conversation = ChatConversation.query.filter_by(
            session_id=session_id
        ).first()
        
        if not conversation:
            logger_service.warning("Conversation not found", session_id=session_id)
            return jsonify({
                'success': False,
                'error': 'Conversation not found'
            }), 404
        
        messages = ChatMessage.query.filter_by(
            conversation_id=conversation.id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        logger_service.info("Conversation history retrieved",
                          session_id=session_id,
                          message_count=len(messages))
        
        return jsonify({
            'success': True,
            'conversation_id': conversation.id,
            'session_id': session_id,
            'messages': [msg.to_dict() for msg in messages],
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        }), 200
    
    except Exception as e:
        logger_service.error("Error retrieving conversation history",
                           session_id=session_id,
                           error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve conversation history'
        }), 500

# Helper functions
def get_or_create_conversation(session_id: str, user_ip: str, user_agent: str):
    """Get existing conversation or create new one"""
    
    conversation = ChatConversation.query.filter_by(
        session_id=session_id, 
        is_active=True
    ).first()
    
    if not conversation:
        conversation = ChatConversation(
            session_id=session_id,
            user_ip=user_ip,
            user_agent=user_agent
        )
        db.session.add(conversation)
        db.session.flush()  # Get the ID
        
        logger_service.info("Created new conversation", 
                          session_id=session_id,
                          conversation_id=conversation.id)
    
    return conversation

def get_conversation_history(conversation_id: int) -> list:
    """Get recent conversation history from database"""
    
    recent_messages = ChatMessage.query.filter_by(
        conversation_id=conversation_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    history = [msg.to_openai_format() for msg in reversed(recent_messages)]
    
    logger_service.trace("Retrieved conversation history", 
                       conversation_id=conversation_id,
                       message_count=len(history))
    
    return history

def get_ai_response_sync(message: str, conversation_history: list) -> dict:
    """Get AI response using service synchronously"""
    
    # Ensure chat service is initialized
    if not chat_service.prompt_engine:
        chat_service.initialize()
    
    # Run async method in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        ai_result = loop.run_until_complete(
            chat_service.get_chat_response(message, conversation_history)
        )
        logger_service.info("AI response generated", 
                          success=ai_result.get('success', False),
                          source=ai_result.get('source', 'unknown'))
        return ai_result
    finally:
        loop.close()

def process_ai_response(ai_result: dict, conversation, session_id: str, response_time: float):
    """Process and save AI response"""
    
    if ai_result['success']:
        # Save successful assistant message
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            message_type='assistant',
            content=ai_result['response'],
            quick_replies=ai_result.get('quick_replies', []),
            tokens_used=ai_result.get('tokens_used', 0),
            model_used=ai_result.get('model_used', 'knowledge_base'),
            response_time=response_time,
            metadata={
                'source': ai_result.get('source', 'unknown'),
                'intent': ai_result.get('intent', 'general')
            }
        )
        db.session.add(assistant_message)
        
        # Update conversation
        conversation.updated_at = datetime.now()
        conversation.message_count = ChatMessage.query.filter_by(
            conversation_id=conversation.id
        ).count() + 1
        
        # Update analytics
        update_analytics(ai_result.get('tokens_used', 0), response_time)
        
        db.session.commit()
        
        logger_service.info("Chat response processed successfully", 
                          session_id=session_id,
                          tokens_used=ai_result.get('tokens_used', 0),
                          response_time=response_time)
        
        return jsonify({
            'success': True,
            'response': ai_result['response'],
            'quick_replies': ai_result.get('quick_replies', []),
            'session_id': session_id,
            'conversation_id': conversation.id,
            'timestamp': datetime.now().isoformat(),
            'tokens_used': ai_result.get('tokens_used', 0),
            'response_time': response_time,
            'source': ai_result.get('source', 'unknown')
        }), 200
    else:
        return get_error_response(session_id, ai_result.get('error', 'AI service error'))

def get_error_response(session_id: str, error_message: str):
    """Generate standardized error response"""
    return jsonify({
        'success': False,
        'error': error_message,
        'response': 'I apologize, but I encountered an error. Please try again.',
        'session_id': session_id,
        'timestamp': datetime.now().isoformat()
    }), 500

def update_analytics(tokens_used: int, response_time: float):
    """Update daily analytics"""
    try:
        today = date.today()
        analytics = ChatAnalytics.query.filter_by(date=today).first()
        
        if not analytics:
            analytics = ChatAnalytics(date=today)
            db.session.add(analytics)
        
        analytics.total_messages += 1
        analytics.total_tokens += tokens_used
        
        # Update average response time
        analytics.avg_response_time = (
            (analytics.avg_response_time * (analytics.total_messages - 1) + response_time) 
            / analytics.total_messages
        )
        
        db.session.commit()
        
        logger_service.trace("Analytics updated",
                           date=str(today),
                           total_messages=analytics.total_messages,
                           tokens_added=tokens_used)
        
    except Exception as e:
        logger_service.error("Failed to update analytics", error=str(e))

# Initialize services on import
try:
    service_registry.initialize_all()
except Exception as e:
    logger_service.error("Failed to initialize services on import", error=str(e)) 