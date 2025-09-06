"""
Flask-Security-Too Authentication Routes
Handles user authentication, registration, and profile management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_security import login_required, current_user, roles_required
from flask_security.utils import hash_password, verify_password

auth_security_bp = Blueprint('auth_security', __name__)

@auth_security_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

@auth_security_bp.route('/admin')
@login_required
@roles_required('admin')
def admin():
    """Admin panel - requires admin role"""
    return render_template('admin.html', user=current_user)

@auth_security_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not verify_password(current_password, current_user.password):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        
        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return render_template('change_password.html')
        
        # Update password
        current_user.password = hash_password(new_password)
        from app import db
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth_security.profile'))
    
    return render_template('change_password.html')

@auth_security_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    
    # Update user profile
    current_user.first_name = first_name
    current_user.last_name = last_name
    
    from app import db
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth_security.profile'))
