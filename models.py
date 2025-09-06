from datetime import datetime

from app import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy import UniqueConstraint


# Flask-Security-Too User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Flask-Security-Too expects 'password' field
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(64), nullable=False, unique=True)  # Flask-Security-Too required field
    
    # Keep existing fields for backward compatibility
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    profile_image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Flask-Security-Too relationships
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
    # Existing relationships
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Flask-Security-Too required methods
    def get_id(self):
        return str(self.id)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)


# Flask-Security-Too Role Model
class Role(RoleMixin, db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


# Association table for user roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)


# OAuth model removed - using Flask-Security-Too instead


# Existing project models with updated foreign keys
class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Changed to Integer for Flask-Security-Too
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.String(20), default='draft')  # draft, in_progress, completed, generating_audio, audio_generated
    
    # Storage and file information
    storage_path = db.Column(db.String(500))  # S3/Wasabi path
    original_filename = db.Column(db.String(200))
    
    # Audio-related fields
    audio_url = db.Column(db.String(500))  # URL to generated audio file
    audio_voice = db.Column(db.String(20), default='alloy')  # TTS voice used
    audio_duration = db.Column(db.Float)  # Duration in minutes
    audio_generated_at = db.Column(db.DateTime)  # When audio was generated
    
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