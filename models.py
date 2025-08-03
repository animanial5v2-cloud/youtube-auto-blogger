from app import db
from datetime import datetime
from sqlalchemy import Text, JSON
import uuid

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User settings stored as JSON
    settings = db.Column(JSON, default=dict)
    
    # Relationships
    posts = db.relationship('BlogPost', backref='user', lazy=True, cascade='all, delete-orphan')

class BlogPost(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Post content
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(Text, nullable=False)
    summary = db.Column(Text, nullable=True)
    
    # Source information
    source_type = db.Column(db.String(50), nullable=False)  # 'youtube', 'topic', 'file'
    source_url = db.Column(db.String(1000), nullable=True)
    source_file_name = db.Column(db.String(255), nullable=True)
    
    # Publishing platform information
    platform = db.Column(db.String(50), default='blogger')
    platform_post_id = db.Column(db.String(255), nullable=True)
    blogger_post_id = db.Column(db.String(100), nullable=True)  # Keep for backward compatibility
    blogger_url = db.Column(db.String(1000), nullable=True)  # Keep for backward compatibility
    is_draft = db.Column(db.Boolean, default=False)
    
    # Metadata
    gemini_model = db.Column(db.String(100), nullable=True)
    writing_tone = db.Column(db.String(100), nullable=True)
    target_audience = db.Column(db.String(200), nullable=True)
    image_source = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(1000), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    posted_at = db.Column(db.DateTime, nullable=True)

class PostQueue(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # Queue item content
    topic_or_url = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'processing', 'completed', 'failed'
    
    # Processing metadata
    error_message = db.Column(Text, nullable=True)
    created_post_id = db.Column(db.String(36), db.ForeignKey('blog_post.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    created_post = db.relationship('BlogPost', backref='queue_item', lazy=True)
