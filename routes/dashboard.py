from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import User, Project
from app import db
from flask_login import current_user
from replit_auth import require_login
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@require_login
def index():
    user = current_user
    logging.info(f"Dashboard access for user: {user.id}")
    
    # Get user's projects
    projects = Project.query.filter_by(user_id=user.id).order_by(Project.updated_at.desc()).all()
    
    # Calculate project statistics
    total_projects = len(projects)
    draft_projects = len([p for p in projects if p.status == 'draft'])
    in_progress_projects = len([p for p in projects if p.status == 'in_progress'])
    completed_projects = len([p for p in projects if p.status == 'completed'])
    
    stats = {
        'total': total_projects,
        'draft': draft_projects,
        'in_progress': in_progress_projects,
        'completed': completed_projects
    }
    
    return render_template('dashboard.html', 
                         user=user,
                         projects=projects,
                         stats=stats)

@dashboard_bp.route('/create_project', methods=['POST'])
@require_login
def create_project():
    user_id = current_user.id
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if not title:
        flash('Project title is required.', 'error')
        return redirect(url_for('dashboard.index'))
    
    try:
        project = Project()
        project.title = title
        project.description = description
        project.user_id = user_id
        project.status = 'draft'
        
        db.session.add(project)
        db.session.commit()
        
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('editor.edit_project', project_id=project.id))
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create project error: {e}")
        flash('Failed to create project. Please try again.', 'error')
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/delete_project/<int:project_id>', methods=['POST'])
@require_login
def delete_project(project_id):
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    try:
        project_title = project.title
        db.session.delete(project)
        db.session.commit()
        
        flash(f'Project "{project_title}" deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete project error: {e}")
        flash('Failed to delete project.', 'error')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/project/<int:project_id>/update_status', methods=['POST'])
@require_login
def update_project_status(project_id):
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    new_status = request.json.get('status')
    if new_status not in ['draft', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        project.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Project status updated to {new_status}'
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Update project status error: {e}")
        return jsonify({'error': 'Failed to update project status'}), 500