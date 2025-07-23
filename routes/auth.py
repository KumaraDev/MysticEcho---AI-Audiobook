from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models import User, PasswordResetToken
from app import db
from services.email_service import send_password_reset_email, send_welcome_email
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        logging.info(f"Login attempt for username: {username}")
        logging.info(f"User found: {user is not None}")
        
        if user:
            password_valid = user.check_password(password)
            logging.info(f"Password valid for {username}: {password_valid}")
            
            if password_valid:
                # Clear any existing session data first
                session.clear()
                
                # Set new session data
                session['user_id'] = user.id
                session['username'] = user.username
                session.permanent = True
                
                flash(f'Welcome back, {user.username}!', 'success')
                logging.info(f"User {username} logged in successfully")
                logging.info(f"Session data set: user_id={session.get('user_id')}, username={session.get('username')}")
                return redirect(url_for('dashboard.index'))
        
        flash('Invalid username or password.', 'error')
        logging.warning(f"Failed login attempt for username: {username}")
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('login.html')
        
        if password and len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('login.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('login.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('login.html')
        
        # Create new user
        try:
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            # Send welcome email
            send_welcome_email(user.email, user.username)
            
            flash(f'Account created successfully! Welcome, {user.username}!', 'success')
            logging.info(f"New user registered: {username}")
            return redirect(url_for('dashboard.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            logging.error(f"Registration error: {e}")
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    flash('You have been logged out successfully.', 'info')
    logging.info(f"User {username} logged out")
    return redirect(url_for('index'))

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Handle forgot password requests"""
    email = request.form.get('email')
    
    logging.info(f"Password reset request for email: {email}")
    
    if not email:
        flash('Please enter your email address.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    logging.info(f"User found for email {email}: {user is not None}")
    
    if user:
        try:
            # Create password reset token
            reset_token = PasswordResetToken(user_id=user.id)
            db.session.add(reset_token)
            db.session.commit()
            
            logging.info(f"Created reset token: {reset_token.token[:8]}... for user {user.username}")
            
            # Send reset email
            try:
                email_sent = send_password_reset_email(user.email, user.username, reset_token.token)
                logging.info(f"Email send result: {email_sent}")
            except Exception as email_error:
                logging.error(f"Email sending failed with error: {email_error}")
                email_sent = False
            
            if email_sent:
                flash('Password reset instructions have been sent to your email.', 'success')
                logging.info(f"Password reset email sent to {email}")
            else:
                flash('Failed to send reset email. Please try again later.', 'error')
                logging.error(f"Failed to send password reset email to {email}")
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again later.', 'error')
            logging.error(f"Password reset error: {e}")
    else:
        # Don't reveal if email exists or not for security
        flash('If an account with that email exists, password reset instructions have been sent.', 'info')
        logging.warning(f"Password reset requested for non-existent email: {email}")
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or not reset_token.is_valid():
        flash('Invalid or expired reset link. Please request a new one.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please fill in all fields.', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('reset_password.html', token=token)
        
        try:
            # Update user password
            user = User.query.get(reset_token.user_id)
            if user:
                user.set_password(password)
                
                # Mark token as used
                reset_token.mark_used()
                
                db.session.commit()
                
                flash('Password successfully reset! You can now log in with your new password.', 'success')
                logging.info(f"Password reset completed for user {user.username}")
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid reset token.', 'error')
                return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while resetting your password. Please try again.', 'error')
            logging.error(f"Password reset completion error: {e}")
    
    return render_template('reset_password.html', token=token)

def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
