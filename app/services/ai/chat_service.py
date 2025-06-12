"""
Enhanced Chat Service for TraintiQ
Handles AI chat conversations with OpenAI integration and knowledge base fallback
Uses proper separation of concerns and professional logging
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# OpenAI imports with error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.core.base_service import BaseService
from app.core.decorators import log_execution_time, handle_exceptions
from app.services.ai.prompt_engine import PromptEngine
from app.services.ai.knowledge_base import KnowledgeBase

class ChatService(BaseService):
    """
    Enhanced Chat Service with proper architecture and logging
    """
    
    def __init__(self):
        super().__init__("ChatService")
        
        # Initialize modules
        self.prompt_engine = None
        self.knowledge_base = None
        self.client = None
        
        # Configuration
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 1500
        self.temperature = 0.7
        
        self.logger.info("ChatService initialized successfully")

    def initialize(self) -> None:
        """Initialize the chat service components"""
        try:
            self.logger.info("Initializing ChatService components...")
            
            # Initialize AI modules
            self.prompt_engine = PromptEngine()
            self.knowledge_base = KnowledgeBase()
            
            # Initialize OpenAI client if available
            if OPENAI_AVAILABLE:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key and api_key.strip():
                    try:
                        self.client = OpenAI(api_key=api_key)
                        self.logger.info("OpenAI client initialized successfully")
                    except Exception as e:
                        self.logger.warning(f"OpenAI client initialization failed: {str(e)}")
                        self.logger.info("Using knowledge base mode instead")
                        self.client = None
                else:
                    self.logger.warning("OpenAI API key not found, using knowledge base mode")
            else:
                self.logger.warning("OpenAI package not available, using knowledge base mode")
            
            self.logger.info("ChatService initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatService: {str(e)}")
            raise

    @log_execution_time
    @handle_exceptions(default_return={"success": False, "error": "Service error"})
    async def get_chat_response(self, message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Get enhanced response from AI with comprehensive logging"""
        
        self.logger.info("Processing chat request", 
                        message_length=len(message),
                        has_history=bool(conversation_history))
        
        try:
            # Analyze intent and check knowledge base
            intent = self.prompt_engine.analyze_message_intent(message)
            self.logger.trace(f"Intent analyzed: {intent}")
            
            knowledge_match = self.knowledge_base.find_best_match(message, intent)
            
            # Use knowledge base if good match found
            if knowledge_match:
                self.logger.info("Knowledge base match found",
                               intent=intent,
                               confidence=knowledge_match.get("confidence", 0))
                
                return {
                    "success": True,
                    "response": knowledge_match["answer"],
                    "quick_replies": knowledge_match["quick_replies"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "knowledge_base",
                    "intent": intent
                }
            
            # Try OpenAI if available
            if self.client:
                return await self._get_openai_response(message, conversation_history, intent)
            
            # Fallback response
            return self._get_fallback_response(intent)
            
        except Exception as e:
            self.logger.error(f"Error processing chat request: {str(e)}")
            return self._get_error_response()

    async def _get_openai_response(self, message: str, conversation_history: List[Dict], intent: str) -> Dict[str, Any]:
        """Get response from OpenAI API"""
        
        self.logger.trace("Calling OpenAI API")
        
        # Prepare messages 
        messages = [
            {"role": "system", "content": self.prompt_engine.generate_system_prompt()}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-10:])
        
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            top_p=0.9,
            stream=False
        )
        
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        self.logger.info("OpenAI response generated", 
                        model=self.model,
                        tokens_used=tokens_used)
        
        return {
            "success": True,
            "response": ai_response,
            "quick_replies": self.prompt_engine.get_contextual_quick_replies(intent),
            "timestamp": datetime.now().isoformat(),
            "model_used": self.model,
            "tokens_used": tokens_used,
            "intent": intent,
            "source": "openai_gpt4"
        }

    def _get_fallback_response(self, intent: str) -> Dict[str, Any]:
        """Generate fallback response when OpenAI is not available"""
        
        self.logger.info("Using fallback response", intent=intent)
        
        quick_replies = self.prompt_engine.get_contextual_quick_replies(intent)
        
        return {
            "success": True,
            "response": "I'd be happy to help you learn about TraintiQ! While I'm getting the specific information you're looking for, here are some topics I can help you with right away.",
            "quick_replies": quick_replies,
            "timestamp": datetime.now().isoformat(),
            "source": "fallback_with_context",
            "intent": intent
        }

    def _get_error_response(self) -> Dict[str, Any]:
        """Generate error response"""
        
        return {
            "success": False,
            "response": "I apologize, but I'm having trouble connecting right now. Our technical team is working on it. Please try again in a few moments or contact our support team at support@traintiq.com.",
            "quick_replies": ["Contact Support", "Try Again", "Technical Help"],
            "timestamp": datetime.now().isoformat(),
            "source": "error_handler"
        }

    @log_execution_time
    def get_conversation_starters(self) -> List[str]:
        """Get conversation starter suggestions"""
        
        starters = [
            "Tell me about TraintiQ services 🚀",
            "What are your pricing plans? 💰", 
            "How can TraintiQ help my company? 🏢",
            "I'd like to schedule a demo 📅",
            "What industries do you serve? 🏭",
            "Tell me about your AI capabilities 🤖"
        ]
        
        self.logger.trace("Generated conversation starters", count=len(starters))
        return starters

    @log_execution_time
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key"""
        
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI package not available")
            return False
            
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or not api_key.strip():
            self.logger.warning("OpenAI API key not configured")
            return False
            
        try:
            # Test API key with a simple call
            test_client = OpenAI(api_key=api_key)
            test_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            self.logger.info("OpenAI API key validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenAI API key validation failed: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Cleanup resources"""
        self.logger.info("Cleaning up ChatService resources")
        self.client = None
        super().cleanup() 