# 🚀 Flask-Security-Too Implementation Plan

## Overview
This document outlines the step-by-step implementation of Flask-Security-Too to replace the current Replit OAuth authentication system in MysticEcho.

## 📋 Prerequisites
- Python 3.11+
- Flask application running
- Database (SQLite/PostgreSQL)
- Email service (Gmail/SendGrid)

## 🎯 Implementation Steps

### **Phase 1: Environment Setup (30 minutes)**

1. **Install Dependencies**
   ```bash
   source venv/bin/activate
   pip install flask-security-too flask-mail flask-wtf
   ```

2. **Update .env.example**
   ```bash
   # Add to .env.example
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   SECURITY_PASSWORD_SALT=your-random-salt-here
   ```

### **Phase 2: Database Models (1 hour)**

1. **Update models.py**
   ```python
   from flask_security import UserMixin, RoleMixin
   from datetime import datetime
   
   # Update existing User model
   class User(UserMixin, db.Model):
       __tablename__ = 'users'
       
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(255), unique=True, nullable=False)
       password_hash = db.Column(db.String(255), nullable=False)
       active = db.Column(db.Boolean(), default=True)
       confirmed_at = db.Column(db.DateTime())
       
       # Keep existing fields
       first_name = db.Column(db.String(255), nullable=True)
       last_name = db.Column(db.String(255), nullable=True)
       profile_image_url = db.Column(db.String(500), nullable=True)
       created_at = db.Column(db.DateTime, default=datetime.now)
       updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
       
       # Relationships
       projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
       roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
   
   # Add Role model
   class Role(RoleMixin, db.Model):
       __tablename__ = 'roles'
       
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(80), unique=True)
       description = db.Column(db.String(255))
   
   # Add user_roles association table
   user_roles = db.Table('user_roles',
       db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
       db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
   )
   ```

2. **Create Migration Script**
   ```python
   # create_migration.py
   from app import app, db
   from models import User, Role, user_roles
   from flask_security import SQLAlchemyUserDatastore
   
   def create_roles():
       with app.app_context():
           user_datastore = SQLAlchemyUserDatastore(db, User, Role)
           
           # Create roles
           admin_role = user_datastore.create_role(name='admin', description='Administrator')
           user_role = user_datastore.create_role(name='user', description='Regular User')
           
           db.session.commit()
           print("Roles created successfully")
   ```

### **Phase 3: Flask-Security Configuration (1 hour)**

1. **Update app.py**
   ```python
   from flask_security import Security, SQLAlchemyUserDatastore
   from flask_mail import Mail
   from models import User, Role
   
   # Initialize Flask-Mail
   mail = Mail(app)
   
   # Configure Flask-Security-Too
   app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT')
   app.config['SECURITY_REGISTERABLE'] = True
   app.config['SECURITY_SEND_REGISTER_EMAIL'] = True
   app.config['SECURITY_EMAIL_SENDER'] = os.environ.get('MAIL_USERNAME')
   app.config['SECURITY_CONFIRMABLE'] = True
   app.config['SECURITY_RECOVERABLE'] = True
   app.config['SECURITY_CHANGEABLE'] = True
   
   # Initialize user datastore
   user_datastore = SQLAlchemyUserDatastore(db, User, Role)
   security = Security(app, user_datastore)
   ```

2. **Create new auth routes**
   ```python
   # routes/auth_new.py
   from flask import Blueprint, render_template, redirect, url_for, flash
   from flask_security import login_required, current_user
   from flask_security.utils import hash_password
   
   auth_new_bp = Blueprint('auth_new', __name__)
   
   @auth_new_bp.route('/login')
   def login():
       return render_template('security/login_user.html')
   
   @auth_new_bp.route('/register')
   def register():
       return render_template('security/register_user.html')
   
   @auth_new_bp.route('/profile')
   @login_required
   def profile():
       return render_template('profile.html', user=current_user)
   ```

### **Phase 4: Templates (2 hours)**

1. **Create base security templates**
   ```html
   <!-- templates/security/login_user.html -->
   {% extends "base.html" %}
   {% block content %}
   <div class="container mt-5">
       <div class="row justify-content-center">
           <div class="col-md-6">
               <div class="card">
                   <div class="card-header">
                       <h3 class="text-center">Sign In</h3>
                   </div>
                   <div class="card-body">
                       <form action="{{ url_for('security.login') }}" method="POST">
                           {{ login_user_form.hidden_tag() }}
                           
                           <div class="mb-3">
                               {{ login_user_form.email.label(class="form-label") }}
                               {{ login_user_form.email(class="form-control") }}
                           </div>
                           
                           <div class="mb-3">
                               {{ login_user_form.password.label(class="form-label") }}
                               {{ login_user_form.password(class="form-control") }}
                           </div>
                           
                           <div class="mb-3 form-check">
                               {{ login_user_form.remember(class="form-check-input") }}
                               {{ login_user_form.remember.label(class="form-check-label") }}
                           </div>
                           
                           <div class="d-grid">
                               {{ login_user_form.submit(class="btn btn-primary") }}
                           </div>
                       </form>
                       
                       <div class="text-center mt-3">
                           <a href="{{ url_for('security.forgot_password') }}">Forgot Password?</a>
                       </div>
                   </div>
               </div>
           </div>
       </div>
   </div>
   {% endblock %}
   ```

2. **Update base template**
   ```html
   <!-- Update templates/base.html -->
   <ul class="navbar-nav">
       {% if current_user.is_authenticated %}
           <li class="nav-item dropdown">
               <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                   <i data-feather="user" class="me-1"></i>{{ current_user.email }}
               </a>
               <ul class="dropdown-menu dropdown-menu-end">
                   <li><a class="dropdown-item" href="{{ url_for('auth_new.profile') }}">
                       <i data-feather="user" class="me-2"></i>Profile
                   </a></li>
                   <li><a class="dropdown-item" href="{{ url_for('security.change_password') }}">
                       <i data-feather="key" class="me-2"></i>Change Password
                   </a></li>
                   <li><hr class="dropdown-divider"></li>
                   <li><a class="dropdown-item" href="{{ url_for('security.logout') }}">
                       <i data-feather="log-out" class="me-2"></i>Logout
                   </a></li>
               </ul>
           </li>
       {% else %}
           <li class="nav-item">
               <a class="nav-link" href="{{ url_for('security.login') }}">
                   <i data-feather="log-in" class="me-1"></i>Sign In
               </a>
           </li>
           <li class="nav-item">
               <a class="nav-link" href="{{ url_for('security.register') }}">
                   <i data-feather="user-plus" class="me-1"></i>Sign Up
               </a>
           </li>
       {% endif %}
   </ul>
   ```

### **Phase 5: Route Protection (30 minutes)**

1. **Update existing routes**
   ```python
   # Replace @require_login with @login_required
   from flask_security import login_required
   
   @dashboard_bp.route('/')
   @login_required  # Instead of @require_login
   def index():
       # ... existing code
   ```

2. **Update main.py**
   ```python
   # Remove Replit auth blueprint
   # app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")
   
   # Add new auth blueprint
   from routes.auth_new import auth_new_bp
   app.register_blueprint(auth_new_bp, url_prefix='/auth')
   ```

### **Phase 6: Data Migration (1 hour)**

1. **Create migration script**
   ```python
   # migrate_users.py
   from app import app, db
   from models import User, Role
   from flask_security import SQLAlchemyUserDatastore
   import secrets
   import string
   
   def generate_random_password():
       return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
   
   def migrate_users():
       with app.app_context():
           user_datastore = SQLAlchemyUserDatastore(db, User, Role)
           
           # Get all existing users
           existing_users = User.query.all()
           
           for user in existing_users:
               if not user.password_hash:  # Only migrate users without passwords
                   # Generate random password
                   temp_password = generate_random_password()
                   
                   # Update user with password
                   user.password_hash = hash_password(temp_password)
                   user.confirmed_at = user.created_at  # Mark as confirmed
                   
                   # Assign user role
                   user_role = Role.query.filter_by(name='user').first()
                   if user_role:
                       user.roles.append(user_role)
                   
                   # Send password reset email
                   send_password_reset_email(user.email, temp_password)
                   
                   print(f"Migrated user: {user.email}")
           
           db.session.commit()
           print("Migration completed!")
   ```

### **Phase 7: Testing (1 hour)**

1. **Test Registration**
   - Create new user account
   - Verify email confirmation
   - Test login/logout

2. **Test Existing Features**
   - Project creation
   - Editor functionality
   - Audio generation
   - All protected routes

3. **Test Migration**
   - Run migration script
   - Verify existing users can login
   - Test password reset

### **Phase 8: Deployment (30 minutes)**

1. **Update Environment Variables**
   ```bash
   # Add to production .env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   SECURITY_PASSWORD_SALT=your-random-salt-here
   ```

2. **Database Migration**
   ```bash
   # Run migration in production
   python migrate_users.py
   ```

3. **Deploy and Monitor**
   - Deploy updated application
   - Monitor for errors
   - Test all functionality

## 🧪 Testing Checklist

- [ ] User registration works
- [ ] Email confirmation works
- [ ] Login/logout works
- [ ] Password reset works
- [ ] All existing routes protected
- [ ] Project creation works
- [ ] Editor functionality works
- [ ] Audio generation works
- [ ] User migration completed
- [ ] No broken links or errors

## 🚨 Rollback Plan

If issues arise:
1. Revert to previous commit
2. Restore Replit auth
3. Investigate issues
4. Fix and retry

## 📊 Success Metrics

- [ ] All users can login with new system
- [ ] No functionality broken
- [ ] Email notifications working
- [ ] Performance maintained
- [ ] Security improved

## ⏱️ Total Implementation Time: 6-8 hours

This implementation plan provides a comprehensive, step-by-step approach to migrating from Replit OAuth to Flask-Security-Too while maintaining all existing functionality.
