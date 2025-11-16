"""
Database models for Learning Log application
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

# Create db instance here to avoid circular imports
db = SQLAlchemy()

# Tag models will be imported after db is defined

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship to topics
    topics = db.relationship('Topic', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Topic(db.Model):
    """Topic model for learning subjects"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship to entries
    entries = db.relationship('Entry', backref='topic', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Topic {self.name}>'

class Entry(db.Model):
    """Entry model for learning log entries"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign key to topic
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    
    def __repr__(self):
        return f'<Entry {self.title}>'

# Association tables for many-to-many relationships
topic_tags = db.Table('topic_tags',
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

entry_tags = db.Table('entry_tags', 
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Category(db.Model):
    """Category model for organizing tags"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6c757d')  # Hex color code
    icon = db.Column(db.String(50), default='bi-tag')   # Bootstrap icon class
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    tags = db.relationship('Tag', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @property
    def tag_count(self):
        """Get count of tags in this category"""
        return len(self.tags)
    
    @property
    def usage_count(self):
        """Get total usage count across all tags in category"""
        return sum(tag.usage_count for tag in self.tags)

class Tag(db.Model):
    """Tag model for labeling topics and entries"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7))  # Optional custom color, inherits from category if None
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('name', 'user_id', name='unique_tag_per_user'),)
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    @property
    def display_color(self):
        """Get display color (custom or inherited from category)"""
        if self.color:
            return self.color
        elif self.category:
            return self.category.color
        return '#6c757d'  # Default gray
    
    @property
    def usage_count(self):
        """Get total usage count (topics + entries)"""
        return len(self.topics) + len(self.entries)
    
    @property
    def topic_count(self):
        """Get count of topics using this tag"""
        return len(self.topics)
    
    @property
    def entry_count(self):
        """Get count of entries using this tag"""
        return len(self.entries)
    
    def can_delete(self):
        """Check if tag can be safely deleted (not used anywhere)"""
        return self.usage_count == 0

# Add many-to-many relationships to existing models
Topic.tags = db.relationship('Tag', secondary=topic_tags, lazy='subquery', backref=db.backref('topics', lazy=True))
Entry.tags = db.relationship('Tag', secondary=entry_tags, lazy='subquery', backref=db.backref('entries', lazy=True))