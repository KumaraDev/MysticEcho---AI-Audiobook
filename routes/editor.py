from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import User, Project, ProjectVersion, Chapter
from app import db
from routes.auth import login_required
from services.ai_service import get_content_suggestions, improve_text
from services.storage_service import save_project_backup
from services.pdf_service import extract_text_from_pdf
import logging
import os

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/project/<int:project_id>')
@login_required
def edit_project(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get recent versions for history
    recent_versions = ProjectVersion.query.filter_by(project_id=project_id).order_by(ProjectVersion.created_at.desc()).limit(5).all()
    
    # Get chapters for project
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
    
    return render_template('editor.html', project=project, versions=recent_versions, chapters=chapters)

@editor_bp.route('/project/<int:project_id>/chapters')
@login_required
def manage_chapters(project_id):
    """Chapter management view"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
    
    return render_template('editor/chapters.html', project=project, chapters=chapters)

@editor_bp.route('/save_project/<int:project_id>', methods=['POST'])
@login_required
def save_project(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    content = request.json.get('content', '') if request.json else ''
    auto_save = request.json.get('auto_save', False) if request.json else False
    
    try:
        # Update project content
        old_content = project.content
        project.content = content
        
        # Create version if content significantly changed and not auto-save
        if not auto_save and old_content != content:
            version_count = ProjectVersion.query.filter_by(project_id=project_id).count()
            version = ProjectVersion()
            version.project_id = project_id
            version.content = content
            version.version_number = version_count + 1
            version.notes = f"Manual save at {project.updated_at}"
            db.session.add(version)
        
        db.session.commit()
        
        # Backup to cloud storage
        if not auto_save:
            try:
                save_project_backup(project)
            except Exception as e:
                logging.warning(f"Cloud backup failed: {e}")
        
        word_count = len(content.split()) if content else 0
        
        return jsonify({
            'success': True,
            'message': 'Project saved successfully',
            'word_count': word_count,
            'auto_save': auto_save
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Save project error: {e}")
        return jsonify({'error': 'Failed to save project'}), 500

# Chapter Management Routes
@editor_bp.route('/project/<int:project_id>/chapter/create', methods=['POST'])
@login_required
def create_chapter(project_id):
    """Create a new chapter"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    title = data.get('title', 'Untitled Chapter')
    
    try:
        # Get the next order index
        max_order = db.session.query(db.func.max(Chapter.order_index)).filter_by(project_id=project_id).scalar() or 0
        
        chapter = Chapter(
            project_id=project_id,
            title=title,
            content='',
            order_index=max_order + 1
        )
        
        db.session.add(chapter)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'chapter': {
                'id': chapter.id,
                'title': chapter.title,
                'content': chapter.content,
                'order_index': chapter.order_index
            }
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create chapter error: {e}")
        return jsonify({'error': 'Failed to create chapter'}), 500

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>', methods=['GET'])
@login_required
def get_chapter(project_id, chapter_id):
    """Get chapter content for editing"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    return jsonify({
        'id': chapter.id,
        'title': chapter.title,
        'content': chapter.content,
        'order_index': chapter.order_index
    })

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>', methods=['PUT'])
@login_required
def update_chapter(project_id, chapter_id):
    """Update chapter content and title"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    data = request.get_json()
    
    try:
        chapter.title = data.get('title', chapter.title)
        chapter.content = data.get('content', chapter.content)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chapter updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Update chapter error: {e}")
        return jsonify({'error': 'Failed to update chapter'}), 500

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>', methods=['DELETE'])
@login_required
def delete_chapter(project_id, chapter_id):
    """Delete a chapter"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    try:
        db.session.delete(chapter)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chapter deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete chapter error: {e}")
        return jsonify({'error': 'Failed to delete chapter'}), 500

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>/move', methods=['POST'])
@login_required
def move_chapter(project_id, chapter_id):
    """Move a chapter up or down in order"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    data = request.get_json()
    direction = data.get('direction')
    
    if direction not in ['up', 'down']:
        return jsonify({'error': 'Invalid direction'}), 400
    
    try:
        # Get all chapters for this project ordered by index
        chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
        
        current_index = chapter.order_index
        
        if direction == 'up' and current_index > 1:
            # Find the chapter with the previous order index
            prev_chapter = next((ch for ch in chapters if ch.order_index == current_index - 1), None)
            if prev_chapter:
                # Swap order indices
                prev_chapter.order_index = current_index
                chapter.order_index = current_index - 1
        elif direction == 'down':
            # Find the chapter with the next order index
            next_chapter = next((ch for ch in chapters if ch.order_index == current_index + 1), None)
            if next_chapter:
                # Swap order indices
                next_chapter.order_index = current_index
                chapter.order_index = current_index + 1
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Move chapter error: {e}")
        return jsonify({'error': 'Failed to move chapter'}), 500

@editor_bp.route('/project/<int:project_id>/chapters/reorder', methods=['POST'])
@login_required
def reorder_chapters(project_id):
    """Reorder chapters via drag and drop"""
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    chapter_order = data.get('chapter_order', [])
    
    try:
        for index, chapter_id in enumerate(chapter_order):
            chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
            if chapter:
                chapter.order_index = index
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chapters reordered successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Reorder chapters error: {e}")
        return jsonify({'error': 'Failed to reorder chapters'}), 500

@editor_bp.route('/ai_suggestions/<int:project_id>', methods=['POST'])
@login_required
def ai_suggestions(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    selected_text = request.json.get('text', '') if request.json else ''
    suggestion_type = request.json.get('type', 'improve') if request.json else 'improve'  # improve, expand, summarize
    
    if not selected_text.strip():
        return jsonify({'error': 'No text selected'}), 400
    
    try:
        if suggestion_type == 'improve':
            suggestions = improve_text(selected_text)
        else:
            suggestions = get_content_suggestions(selected_text, suggestion_type)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'original_text': selected_text
        })
        
    except Exception as e:
        logging.error(f"AI suggestions error: {e}")
        return jsonify({'error': 'Failed to generate AI suggestions. Please check your API configuration.'}), 500

@editor_bp.route('/ai_preview/<int:project_id>')
@login_required
def ai_preview(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get suggestions from session (passed from editor)
    suggestions = session.get('ai_suggestions', {})
    
    return render_template('ai_preview.html', project=project, suggestions=suggestions)

@editor_bp.route('/upload_pdf/<int:project_id>', methods=['POST'])
@login_required
def upload_pdf(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['pdf_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file.filename and not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save file temporarily
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename or 'uploaded_file.pdf')
        file.save(file_path)
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_path)
        
        # Clean up temporary file
        os.remove(file_path)
        
        if not extracted_text.strip():
            return jsonify({'error': 'No text could be extracted from the PDF'}), 400
        
        # Append to project content
        if project.content:
            project.content += '\n\n--- Imported from PDF ---\n\n' + extracted_text
        else:
            project.content = extracted_text
        
        project.original_filename = file.filename or 'uploaded_file.pdf'
        db.session.commit()
        
        word_count = len(extracted_text.split())
        
        return jsonify({
            'success': True,
            'message': f'PDF imported successfully. {word_count} words extracted.',
            'extracted_text': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text
        })
        
    except Exception as e:
        logging.error(f"PDF upload error: {e}")
        return jsonify({'error': 'Failed to process PDF file'}), 500

@editor_bp.route('/update_status/<int:project_id>', methods=['POST'])
@login_required
def update_status(project_id):
    user_id = session.get('user_id')
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    new_status = request.json.get('status') if request.json else None
    
    if new_status not in ['draft', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        project.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Project status updated to {new_status.replace("_", " ").title()}'
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Status update error: {e}")
        return jsonify({'error': 'Failed to update status'}), 500
