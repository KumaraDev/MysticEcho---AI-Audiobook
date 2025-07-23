from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to projects
    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('chapters', order_by='Chapter.order_index', lazy=True))
    
    def __repr__(self):
        return f'<Chapter {self.title}>'

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='reset_tokens')
    
    def __init__(self, user_id, hours=1):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_used(self):
        self.used = True
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token[:8]}...>'
