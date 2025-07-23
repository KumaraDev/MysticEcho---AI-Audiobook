from datetime import datetime

from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           onupdate=datetime.now)
    
    # Relationships - update foreign key to use String
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')


# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)


# Existing project models with updated foreign keys
class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, default='')
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)  # Changed to String
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.String(20), default='draft')  # draft, in_progress, completed
    
    # Storage and file information
    storage_path = db.Column(db.String(500))  # S3/Wasabi path
    original_filename = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Project {self.title}>'


class ProjectVersion(db.Model):
    __tablename__ = 'project_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)  # For chapter-specific versions
    title = db.Column(db.String(200))  # Chapter title at time of version
    content = db.Column(db.Text, nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    word_count = db.Column(db.Integer, default=0)  # Track word count
    created_at = db.Column(db.DateTime, default=datetime.now)
    notes = db.Column(db.Text)
    
    project = db.relationship('Project', backref='versions')
    chapter = db.relationship('Chapter', backref='versions')
    
    def __repr__(self):
        return f'<ProjectVersion {self.project_id}:{self.version_number}>'


class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    order_index = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = db.relationship('Project', backref='chapters')
    
    def __repr__(self):
        return f'<Chapter {self.title}>'