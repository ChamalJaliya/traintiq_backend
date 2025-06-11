"""
Enhanced Chat Routes for TraintiQ
Uses improved architecture with proper logging and service management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_restx import Api, Resource, fields, Namespace
from app.services.chat_service import ChatService
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

# Create blueprint with proper logging
chat_bp = Blueprint('chat', __name__)
api = Api(chat_bp, doc='/chat/docs/', title='TraintiQ Chat API', description='Professional Chat API with AI Assistant')

# Create namespace
chat_ns = Namespace('chat', description='Chat operations with AI assistant')

# Request/Response models for API documentation
chat_request_model = api.model('ChatRequest', {
    'message': fields.String(required=True, description='User message'),
    'session_id': fields.String(required=False, description='Chat session ID'),
    'conversation_history': fields.List(fields.Raw, required=False, description='Previous conversation context')
})

chat_response_model = api.model('ChatResponse', {
    'success': fields.Boolean(description='Whether the request was successful'),
    'response': fields.String(description='AI assistant response'),
    'quick_replies': fields.List(fields.String, description='Suggested quick replies'),
    'session_id': fields.String(description='Chat session ID'),
    'conversation_id': fields.Integer(description='Database conversation ID'),
    'timestamp': fields.String(description='Response timestamp'),
    'tokens_used': fields.Integer(description='Number of tokens used'),
    'response_time': fields.Float(description='Response time in seconds'),
    'source': fields.String(description='Response source (openai/knowledge_base/fallback)')
})

# Initialize and register chat service
chat_service = ChatService()
service_registry.register_service(chat_service, 'chat_service')

@chat_ns.route('/message')
class ChatMessageResource(Resource):
    @with_request_id
    @rate_limit(max_requests=50, time_window=3600)  # 50 requests per hour
    @log_execution_time
    @chat_ns.expect(chat_request_model)
    @chat_ns.marshal_with(chat_response_model)
    def post(self):
        """Send a message to the AI assistant with enhanced logging and error handling"""
        
        start_time = time.time()
        session_id = None
        conversation = None
        
        try:
            # Validate and extract request data
            data = request.get_json()
            
            if not data or 'message' not in data:
                logger_service.warning("Chat request missing message field")
                return {
                    'success': False,
                    'error': 'Message is required',
                    'response': 'Please provide a message to continue our conversation.'
                }, 400
            
            message = data['message'].strip()
            if not message:
                logger_service.warning("Chat request with empty message")
                return {
                    'success': False,
                    'error': 'Message cannot be empty',
                    'response': 'Please enter a message to start our conversation.'
                }, 400
            
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
            conversation = self._get_or_create_conversation(session_id, user_ip, user_agent)
            
            # Save user message
            user_message = ChatMessage(
                conversation_id=conversation.id,
                message_type='user',
                content=message
            )
            db.session.add(user_message)
            
            # Get conversation history if not provided
            if not conversation_history:
                conversation_history = self._get_conversation_history(conversation.id)
            
            # Get AI response
            ai_result = self._get_ai_response_sync(message, conversation_history)
            
            response_time = time.time() - start_time
            
            # Process and save response
            return self._process_ai_response(
                ai_result, conversation, session_id, response_time
            )
        
        except SQLAlchemyError as e:
            db.session.rollback()
            logger_service.error("Database error in chat endpoint", 
                               session_id=session_id,
                               error=str(e))
            return self._get_error_response(session_id, "Database error occurred")
        
        except Exception as e:
            db.session.rollback()
            logger_service.error("Unexpected error in chat endpoint",
                               session_id=session_id,
                               error=str(e))
            return self._get_error_response(session_id, "An unexpected error occurred")
    
    def _get_or_create_conversation(self, session_id: str, user_ip: str, user_agent: str) -> ChatConversation:
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
    
    def _get_conversation_history(self, conversation_id: int) -> list:
        """Get recent conversation history from database"""
        
        recent_messages = ChatMessage.query.filter_by(
            conversation_id=conversation_id
        ).order_by(ChatMessage.created_at.desc()).limit(10).all()
        
        history = [msg.to_openai_format() for msg in reversed(recent_messages)]
        
        logger_service.trace("Retrieved conversation history", 
                           conversation_id=conversation_id,
                           message_count=len(history))
        
        return history
    
    def _get_ai_response_sync(self, message: str, conversation_history: list) -> dict:
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
    
    def _process_ai_response(self, ai_result: dict, conversation: ChatConversation, 
                           session_id: str, response_time: float) -> tuple:
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
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            
            # Commit changes
            db.session.commit()
            
            # Update analytics
            self._update_analytics(ai_result.get('tokens_used', 0), response_time)
            
            logger_service.info("Chat response processed successfully",
                              session_id=session_id,
                              tokens_used=ai_result.get('tokens_used', 0),
                              response_time=response_time)
            
            return {
                'success': True,
                'response': ai_result['response'],
                'quick_replies': ai_result.get('quick_replies', []),
                'session_id': session_id,
                'conversation_id': conversation.id,
                'timestamp': ai_result['timestamp'],
                'tokens_used': ai_result.get('tokens_used', 0),
                'response_time': response_time,
                'source': ai_result.get('source', 'unknown')
            }
        else:
            # Handle error response
            assistant_message = ChatMessage(
                conversation_id=conversation.id,
                message_type='assistant',
                content=ai_result['response'],
                quick_replies=ai_result.get('quick_replies', []),
                response_time=response_time,
                metadata={'error': ai_result.get('error', 'Unknown error')}
            )
            db.session.add(assistant_message)
            db.session.commit()
            
            logger_service.warning("Chat response contained error",
                                 session_id=session_id,
                                 error=ai_result.get('error', 'Unknown'))
            
            return {
                'success': False,
                'response': ai_result['response'],
                'quick_replies': ai_result.get('quick_replies', []),
                'session_id': session_id,
                'conversation_id': conversation.id,
                'timestamp': ai_result['timestamp'],
                'error': ai_result.get('error', 'Unknown error')
            }, 500
    
    def _get_error_response(self, session_id: str, error_message: str) -> tuple:
        """Generate standardized error response"""
        
        return {
            'success': False,
            'error': error_message,
            'response': 'I apologize, but there was a technical issue. Please try again or contact our support team.',
            'quick_replies': ['Try Again', 'Contact Support', 'Technical Help'],
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }, 500
    
    def _update_analytics(self, tokens_used: int, response_time: float):
        """Update daily analytics with enhanced logging"""
        try:
            today = date.today()
            analytics = ChatAnalytics.query.filter_by(date=today).first()
            
            if not analytics:
                analytics = ChatAnalytics(
                    date=today,
                    total_conversations=0,
                    total_messages=0,
                    total_tokens=0,
                    avg_response_time=0.0
                )
                db.session.add(analytics)
            
            # Update metrics
            analytics.total_messages += 1
            analytics.total_tokens += tokens_used
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

@chat_ns.route('/conversation/<string:session_id>')
class ConversationHistory(Resource):
    @with_request_id
    @log_execution_time
    def get(self, session_id):
        """Get conversation history for a session"""
        
        try:
            logger_service.info("Retrieving conversation history", session_id=session_id)
            
            conversation = ChatConversation.query.filter_by(
                session_id=session_id
            ).first()
            
            if not conversation:
                logger_service.warning("Conversation not found", session_id=session_id)
                return {
                    'success': False,
                    'error': 'Conversation not found'
                }, 404
            
            messages = ChatMessage.query.filter_by(
                conversation_id=conversation.id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            logger_service.info("Conversation history retrieved",
                              session_id=session_id,
                              message_count=len(messages))
            
            return {
                'success': True,
                'conversation_id': conversation.id,
                'session_id': session_id,
                'messages': [msg.to_dict() for msg in messages],
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            }
        
        except Exception as e:
            logger_service.error("Error retrieving conversation history",
                               session_id=session_id,
                               error=str(e))
            return {
                'success': False,
                'error': 'Failed to retrieve conversation history'
            }, 500

@chat_ns.route('/starters')
class ConversationStarters(Resource):
    @log_execution_time
    def get(self):
        """Get conversation starters"""
        
        try:
            # Ensure chat service is initialized
            if not chat_service.prompt_engine:
                chat_service.initialize()
            
            starters = chat_service.get_conversation_starters()
            
            logger_service.trace("Conversation starters retrieved", count=len(starters))
            
            return {
                'success': True,
                'starters': starters
            }
        
        except Exception as e:
            logger_service.error("Error retrieving conversation starters", error=str(e))
            return {
                'success': False,
                'error': 'Failed to retrieve conversation starters'
            }, 500

@chat_ns.route('/health')
class ChatHealth(Resource):
    @log_execution_time
    def get(self):
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
            if chat_service.validate_api_key():
                service_status['openai_api'] = 'healthy'
            else:
                service_status['openai_api'] = 'unavailable'
            
            # Overall health
            overall_healthy = all(
                status in ['healthy', 'unknown', 'unavailable'] 
                for status in service_status.values()
            )
            
            logger_service.info("Health check performed", **service_status)
            
            return {
                'success': True,
                'status': 'healthy' if overall_healthy else 'degraded',
                'services': service_status,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger_service.error("Health check failed", error=str(e))
            return {
                'success': False,
                'status': 'unhealthy',
                'error': str(e)
            }, 500

@chat_ns.route('/analytics')
class ChatAnalyticsResource(Resource):
    @log_execution_time
    def get(self):
        """Get chat analytics data"""
        
        try:
            # Get recent analytics (last 30 days)
            recent_analytics = ChatAnalytics.query.order_by(
                ChatAnalytics.date.desc()
            ).limit(30).all()
            
            # Calculate totals
            total_conversations = sum(a.total_conversations for a in recent_analytics)
            total_messages = sum(a.total_messages for a in recent_analytics)
            total_tokens = sum(a.total_tokens for a in recent_analytics)
            
            avg_response_time = (
                sum(a.avg_response_time for a in recent_analytics) / len(recent_analytics)
                if recent_analytics else 0
            )
            
            logger_service.info("Analytics retrieved",
                              days=len(recent_analytics),
                              total_messages=total_messages)
            
            return {
                'success': True,
                'summary': {
                    'total_conversations': total_conversations,
                    'total_messages': total_messages,
                    'total_tokens': total_tokens,
                    'avg_response_time': round(avg_response_time, 3),
                    'days_analyzed': len(recent_analytics)
                },
                'daily_data': [
                    {
                        'date': a.date.isoformat(),
                        'conversations': a.total_conversations,
                        'messages': a.total_messages,
                        'tokens': a.total_tokens,
                        'avg_response_time': a.avg_response_time
                    }
                    for a in recent_analytics
                ]
            }
        
        except Exception as e:
            logger_service.error("Error retrieving analytics", error=str(e))
            return {
                'success': False,
                'error': 'Failed to retrieve analytics'
            }, 500

# Register namespace
api.add_namespace(chat_ns)

# Initialize services on import
try:
    service_registry.initialize_all()
except Exception as e:
    logger_service.error("Failed to initialize services on import", error=str(e)) 