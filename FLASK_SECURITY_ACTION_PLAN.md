# 🚀 Flask-Security-Too Integration Action Plan

## 📋 **Project Overview**
**Goal:** Replace Replit OAuth with Flask-Security-Too for independent authentication
**Timeline:** 3-4 days
**Risk Level:** Medium (requires careful migration)

---

## 🎯 **Phase 1: Setup and Dependencies (Day 1)**

### **Task 1.1: Install Dependencies**
```bash
# Install Flask-Security-Too and required packages
pip install flask-security-too
pip install flask-mail
pip install flask-wtf
pip install email-validator
```

### **Task 1.2: Update Environment Variables**
```bash
# Add to .env file
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
SECURITY_PASSWORD_SALT=your-random-salt-here
SECURITY_EMAIL_SENDER=your-email@gmail.com
```

### **Task 1.3: Create Backup**
```bash
# Create database backup before migration
cp mystic_echo.db mystic_echo_backup_$(date +%Y%m%d_%H%M%S).db
```

---

## 🗄️ **Phase 2: Database Migration (Day 1-2)**

### **Task 2.1: Update User Model**
```python
# Update models.py
from flask_security import UserMixin, RoleMixin
from datetime import datetime

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

class Role(RoleMixin, db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# Association table
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)
```

### **Task 2.2: Create Migration Script**
```python
# create_migration.py
from app import app, db
from models import User, Role, user_roles
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
import secrets
import string

def generate_random_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

def migrate_users():
    with app.app_context():
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        
        # Create roles
        admin_role = user_datastore.create_role(name='admin', description='Administrator')
        user_role = user_datastore.create_role(name='user', description='Regular User')
        
        # Migrate existing users
        existing_users = User.query.all()
        for user in existing_users:
            if not user.password_hash:
                temp_password = generate_random_password()
                user.password_hash = hash_password(temp_password)
                user.confirmed_at = user.created_at
                user.roles.append(user_role)
                print(f"Migrated user: {user.email}")
        
        db.session.commit()
        print("Migration completed!")
```

---

## ⚙️ **Phase 3: Flask-Security Configuration (Day 2)**

### **Task 3.1: Update app.py**
```python
# Add to app.py
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
app.config['SECURITY_TWO_FACTOR'] = False  # Enable later if needed
app.config['SECURITY_TWO_FACTOR_ENABLED_METHODS'] = ['authenticator']

# Initialize user datastore
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
```

### **Task 3.2: Create New Auth Routes**
```python
# routes/auth_security.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_security import login_required, current_user

auth_security_bp = Blueprint('auth_security', __name__)

@auth_security_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth_security_bp.route('/admin')
@login_required
def admin():
    if not current_user.has_role('admin'):
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('dashboard.index'))
    return render_template('admin.html')
```

---

## 🎨 **Phase 4: Templates and UI (Day 2-3)**

### **Task 4.1: Create Security Templates**
```html
<!-- templates/security/login_user.html -->
{% extends "base.html" %}
{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h3 class="text-center">Sign In to MysticEcho</h3>
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
                        <br>
                        <a href="{{ url_for('security.register') }}">Don't have an account? Sign up</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### **Task 4.2: Update Base Template**
```html
<!-- Update templates/base.html navigation -->
<ul class="navbar-nav">
    {% if current_user.is_authenticated %}
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                <i data-feather="user" class="me-1"></i>{{ current_user.email }}
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="{{ url_for('auth_security.profile') }}">
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

---

## 🔄 **Phase 5: Route Protection Migration (Day 3)**

### **Task 5.1: Update Route Decorators**
```python
# Replace in all route files
from flask_security import login_required

# OLD: @require_login
# NEW: @login_required

@dashboard_bp.route('/')
@login_required  # Changed from @require_login
def index():
    # ... existing code

@editor_bp.route('/project/<int:project_id>')
@login_required  # Changed from @require_login
def edit_project(project_id):
    # ... existing code
```

### **Task 5.2: Update main.py**
```python
# Remove Replit auth
# app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Add new auth blueprint
from routes.auth_security import auth_security_bp
app.register_blueprint(auth_security_bp, url_prefix='/auth')
```

---

## 🗑️ **Phase 6: Remove Old Auth System (Day 3-4)**

### **Task 6.1: Remove Replit Dependencies**
```python
# Remove from app.py
# from replit_auth import require_login, make_replit_blueprint

# Remove from main.py
# from replit_auth import require_login, make_replit_blueprint
# app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")
```

### **Task 6.2: Clean Up Files**
```bash
# Files to remove or clean up
rm replit_auth.py  # After confirming new auth works
# Remove OAuth model from models.py
# Remove Replit-specific environment variables
```

### **Task 6.3: Update Dependencies**
```bash
# Remove from requirements.txt
# flask-dance
# oauthlib
# pyjwt
```

---

## 🧪 **Phase 7: Testing and QA (Day 4)**

### **Task 7.1: Functional Tests**
```python
# tests/test_auth.py
import pytest
from app import app, db
from models import User, Role

def test_user_registration():
    """Test user can register with email and password"""
    with app.test_client() as client:
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        })
        assert response.status_code == 302  # Redirect after registration
        assert User.query.filter_by(email='test@example.com').first() is not None

def test_user_login():
    """Test user can login with correct credentials"""
    with app.test_client() as client:
        # First register a user
        client.post('/register', data={
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        })
        
        # Then login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        assert response.status_code == 302  # Redirect after login

def test_protected_route_access():
    """Test protected routes require authentication"""
    with app.test_client() as client:
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.location

def test_password_reset():
    """Test password reset functionality"""
    with app.test_client() as client:
        response = client.post('/reset', data={
            'email': 'test@example.com'
        })
        assert response.status_code == 200
        # Check email was sent (mock email service)
```

### **Task 7.2: Integration Tests**
```python
# tests/test_integration.py
def test_full_user_workflow():
    """Test complete user workflow from registration to project creation"""
    with app.test_client() as client:
        # 1. Register user
        client.post('/register', data={
            'email': 'test@example.com',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        })
        
        # 2. Login
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword123'
        })
        
        # 3. Access dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        
        # 4. Create project
        response = client.post('/dashboard/create_project', data={
            'title': 'Test Project',
            'description': 'Test Description'
        })
        assert response.status_code == 302  # Redirect after creation
        
        # 5. Access editor
        response = client.get('/editor/project/1')
        assert response.status_code == 200
```

---

## 📋 **QA Functional Test Checklist**

### **Authentication Tests**
- [ ] User can register with email and password
- [ ] User receives email confirmation
- [ ] User can login with correct credentials
- [ ] User cannot login with incorrect credentials
- [ ] User can reset password
- [ ] User can change password
- [ ] User can logout
- [ ] Session persists across browser refresh
- [ ] Session expires after timeout

### **Authorization Tests**
- [ ] Protected routes redirect to login when not authenticated
- [ ] Authenticated users can access protected routes
- [ ] Admin routes require admin role
- [ ] Users can only access their own projects
- [ ] Users cannot access other users' projects

### **Integration Tests**
- [ ] Complete user registration workflow
- [ ] Complete user login workflow
- [ ] Project creation after authentication
- [ ] Editor access after authentication
- [ ] Audio generation after authentication
- [ ] All existing features work with new auth

### **Security Tests**
- [ ] Passwords are hashed securely
- [ ] CSRF protection is enabled
- [ ] Session cookies are secure
- [ ] Email verification is required
- [ ] Password reset tokens expire
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities

### **Performance Tests**
- [ ] Login response time < 500ms
- [ ] Registration response time < 1s
- [ ] Dashboard load time < 2s
- [ ] Editor load time < 3s
- [ ] No memory leaks during auth operations

---

## 🚨 **Rollback Plan**

### **If Issues Arise:**
1. **Immediate Rollback:**
   ```bash
   # Restore database backup
   cp mystic_echo_backup_YYYYMMDD_HHMMSS.db mystic_echo.db
   
   # Revert to previous commit
   git checkout HEAD~1
   ```

2. **Investigate Issues:**
   - Check logs for error messages
   - Test individual components
   - Fix issues in development
   - Retry deployment

3. **Gradual Rollout:**
   - Deploy with both auth systems
   - Route new users to new auth
   - Migrate existing users gradually
   - Remove old auth when stable

---

## 📊 **Success Metrics**

### **Technical Metrics**
- [ ] All tests pass
- [ ] No broken functionality
- [ ] Performance maintained
- [ ] Security improved
- [ ] Code coverage > 80%

### **User Experience Metrics**
- [ ] Registration process < 2 minutes
- [ ] Login process < 30 seconds
- [ ] Password reset < 5 minutes
- [ ] No user complaints
- [ ] All features accessible

### **Business Metrics**
- [ ] User retention maintained
- [ ] No data loss
- [ ] Zero downtime
- [ ] Reduced support tickets
- [ ] Improved security posture

---

## ⏱️ **Timeline Summary**

| Phase | Duration | Tasks | Dependencies |
|-------|----------|-------|--------------|
| **Phase 1** | 4 hours | Setup, Dependencies, Backup | None |
| **Phase 2** | 6 hours | Database Migration | Phase 1 |
| **Phase 3** | 4 hours | Flask-Security Config | Phase 2 |
| **Phase 4** | 6 hours | Templates, UI | Phase 3 |
| **Phase 5** | 4 hours | Route Protection | Phase 4 |
| **Phase 6** | 2 hours | Remove Old Auth | Phase 5 |
| **Phase 7** | 8 hours | Testing, QA | All phases |
| **Total** | **34 hours** | **~4.5 days** | |

---

## 🎯 **Ready to Start?**

This action plan provides a comprehensive roadmap for migrating from Replit OAuth to Flask-Security-Too. Each phase builds on the previous one, ensuring a smooth transition while maintaining all existing functionality.

**Next Step:** Begin with Phase 1 - Setup and Dependencies! 🚀
