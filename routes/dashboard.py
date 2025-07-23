from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Project
from app import db
from routes.auth import login_required
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    logging.info(f"Dashboard access - user_id from session: {user_id}")
    logging.info(f"Session data: {dict(session)}")
    
    user = User.query.get(user_id)
    
    if not user:
        logging.error(f"User not found for user_id: {user_id}")
        flash('User not found.', 'error')
        return redirect(url_for('auth.logout'))
    
    # Get user's projects
    projects = Project.query.filter_by(user_id=user_id).order_by(Project.updated_at.desc()).all()
    
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
    
    return render_template('dashboard.html', user=user, projects=projects, stats=stats)

@dashboard_bp.route('/create_project', methods=['POST'])
@login_required
def create_project():
    user_id = session.get('user_id')
    title = request.form.get('title')
    description = request.form.get('description', '')
    
    if not title:
        flash('Project title is required.', 'error')
        return redirect(url_for('dashboard.index'))
    
    try:
        project = Project()
        project.title = title
        project.description = description
        project.user_id = user_id
        project.content = '# ' + title + '\n\nStart writing your audiobook here...'
        db.session.add(project)
        db.session.commit()
        
        flash(f'Project "{title}" created successfully!', 'success')
        logging.info(f"New project created: {title} by user {user_id}")
        return redirect(url_for('editor.edit_project', project_id=project.id))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while creating the project.', 'error')
        logging.error(f"Project creation error: {e}")
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/delete_project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    try:
        # Delete from storage if exists
        from services.storage_service import delete_project_files
        delete_project_files(project)
        
        db.session.delete(project)
        db.session.commit()
        
        flash(f'Project "{project.title}" deleted successfully.', 'success')
        logging.info(f"Project deleted: {project.title} by user {user_id}")
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the project.', 'error')
        logging.error(f"Project deletion error: {e}")
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/project_stats')
@login_required
def project_stats():
    """API endpoint for project statistics"""
    user_id = session.get('user_id')
    projects = Project.query.filter_by(user_id=user_id).all()
    
    stats = {
        'total_projects': len(projects),
        'total_words': sum(len(p.content.split()) for p in projects if p.content),
        'projects_by_status': {
            'draft': len([p for p in projects if p.status == 'draft']),
            'in_progress': len([p for p in projects if p.status == 'in_progress']),
            'completed': len([p for p in projects if p.status == 'completed'])
        }
    }
    
    return jsonify(stats)
