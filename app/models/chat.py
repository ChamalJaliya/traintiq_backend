from app import db
from datetime import datetime
import json

class ChatConversation(db.Model):
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, index=True)
    user_ip = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship with messages
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'message_count': len(self.messages)
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id'), nullable=False)
    message_type = db.Column(db.Enum('user', 'assistant', name='message_types'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    quick_replies = db.Column(db.JSON, nullable=True)  # Store quick reply options as JSON
    tokens_used = db.Column(db.Integer, nullable=True)
    model_used = db.Column(db.String(50), nullable=True)
    response_time = db.Column(db.Float, nullable=True)  # Response time in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional metadata
    message_metadata = db.Column(db.JSON, nullable=True)  # Store additional metadata as JSON
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'message_type': self.message_type,
            'content': self.content,
            'quick_replies': self.quick_replies,
            'tokens_used': self.tokens_used,
            'model_used': self.model_used,
            'response_time': self.response_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.message_metadata
        }
    
    def to_openai_format(self):
        """Convert message to OpenAI API format"""
        role = 'user' if self.message_type == 'user' else 'assistant'
        return {
            'role': role,
            'content': self.content
        }

class ChatAnalytics(db.Model):
    __tablename__ = 'chat_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_conversations = db.Column(db.Integer, default=0)
    total_messages = db.Column(db.Integer, default=0)
    total_tokens_used = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float, nullable=True)
    unique_sessions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_conversations': self.total_conversations,
            'total_messages': self.total_messages,
            'total_tokens_used': self.total_tokens_used,
            'avg_response_time': self.avg_response_time,
            'unique_sessions': self.unique_sessions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 