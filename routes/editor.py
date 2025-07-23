from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import User, Project, ProjectVersion, Chapter
from app import db
from replit_auth import require_login
from services.ai_service import get_content_suggestions, improve_text
from services.storage_service import save_project_backup
from services.pdf_service import extract_text_from_pdf
from flask_login import current_user
import logging
import os
from datetime import datetime

editor_bp = Blueprint('editor', __name__)

@editor_bp.route('/project/<int:project_id>')
@require_login
def edit_project(project_id):
    user_id = current_user.id
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
@require_login
def manage_chapters(project_id):
    """Chapter management view"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    chapters = Chapter.query.filter_by(project_id=project_id).order_by(Chapter.order_index).all()
    
    return render_template('editor/chapters.html', project=project, chapters=chapters)

@editor_bp.route('/save_project/<int:project_id>', methods=['POST'])
@require_login
def save_project(project_id):
    user_id = current_user.id
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
@require_login
def create_chapter(project_id):
    """Create a new chapter"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    title = data.get('title', 'Untitled Chapter')
    
    try:
        # Get the next order index
        max_order = db.session.query(db.func.max(Chapter.order_index)).filter_by(project_id=project_id).scalar() or 0
        
        chapter = Chapter()
        chapter.project_id = project_id
        chapter.title = title
        chapter.content = ''
        chapter.order_index = max_order + 1
        
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
@require_login
def get_chapter(project_id, chapter_id):
    """Get chapter content for editing"""
    user_id = current_user.id
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
@require_login
def update_chapter(project_id, chapter_id):
    """Update chapter content and title"""
    user_id = current_user.id
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
@require_login
def delete_chapter(project_id, chapter_id):
    """Delete a chapter"""
    user_id = current_user.id
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
@require_login
def move_chapter(project_id, chapter_id):
    """Move a chapter up or down in order"""
    user_id = current_user.id
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
@require_login
def reorder_chapters(project_id):
    """Reorder chapters via drag and drop"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    new_order = data.get('order', [])
    
    if not new_order:
        return jsonify({'error': 'No order data provided'}), 400
    
    try:
        # Update the order_index for each chapter
        for item in new_order:
            chapter_id = item.get('id')
            new_order_index = item.get('order')
            
            chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
            if chapter:
                chapter.order_index = new_order_index
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Reorder chapters error: {e}")
        return jsonify({'error': 'Failed to reorder chapters'}), 500

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>/auto-save', methods=['POST'])
@require_login
def auto_save_chapter(project_id, chapter_id):
    """Auto-save chapter content and create versions"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        # Check if content has significantly changed to create a new version
        content_changed = chapter.content != content
        title_changed = chapter.title != title
        should_create_version = content_changed or title_changed
        
        # Update chapter
        chapter.title = title
        chapter.content = content
        chapter.updated_at = datetime.now()
        
        new_version_created = False
        
        # Create new version if content changed significantly
        if should_create_version:
            # Get the latest version number
            latest_version = ProjectVersion.query.filter_by(
                project_id=project_id, 
                chapter_id=chapter_id
            ).order_by(ProjectVersion.version_number.desc()).first()
            
            next_version_number = (latest_version.version_number + 1) if latest_version else 1
            
            # Create new version
            new_version = ProjectVersion()
            new_version.project_id = project_id
            new_version.chapter_id = chapter_id
            new_version.version_number = next_version_number
            new_version.title = title
            new_version.content = content
            new_version.word_count = len(content.split()) if content else 0
            new_version.created_at = datetime.now()
            
            db.session.add(new_version)
            new_version_created = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_version': new_version_created,
            'word_count': len(content.split()) if content else 0
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Auto-save chapter error: {e}")
        return jsonify({'error': 'Failed to auto-save chapter'}), 500

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>/versions', methods=['GET'])
@require_login
def get_chapter_versions(project_id, chapter_id):
    """Get version history for a chapter"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    try:
        versions = ProjectVersion.query.filter_by(
            project_id=project_id,
            chapter_id=chapter_id
        ).order_by(ProjectVersion.created_at.desc()).limit(10).all()
        
        versions_data = []
        for version in versions:
            versions_data.append({
                'id': version.id,
                'version_number': version.version_number,
                'created_at': version.created_at.isoformat(),
                'word_count': version.word_count
            })
        
        return jsonify(versions_data)
        
    except Exception as e:
        logging.error(f"Get chapter versions error: {e}")
        return jsonify({'error': 'Failed to load versions'}), 500

@editor_bp.route('/project/<int:project_id>/version/<int:version_id>/diff', methods=['GET'])
@require_login
def get_version_diff(project_id, version_id):
    """Get diff between version and current content"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    version = ProjectVersion.query.filter_by(id=version_id, project_id=project_id).first()
    if not version:
        return jsonify({'error': 'Version not found'}), 404
    
    try:
        # Get current chapter content
        chapter = Chapter.query.filter_by(id=version.chapter_id, project_id=project_id).first()
        current_content = chapter.content if chapter else ""
        version_content = version.content or ""
        
        # Simple diff implementation
        diff_html = create_simple_diff(version_content, current_content)
        
        return jsonify({
            'version_number': version.version_number,
            'created_at': version.created_at.isoformat(),
            'diff_html': diff_html
        })
        
    except Exception as e:
        logging.error(f"Get version diff error: {e}")
        return jsonify({'error': 'Failed to generate diff'}), 500

@editor_bp.route('/project/<int:project_id>/chapter/<int:chapter_id>/rollback/<int:version_id>', methods=['POST'])
@require_login
def rollback_to_version(project_id, chapter_id, version_id):
    """Rollback chapter to a specific version"""
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    chapter = Chapter.query.filter_by(id=chapter_id, project_id=project_id).first()
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    version = ProjectVersion.query.filter_by(id=version_id, project_id=project_id, chapter_id=chapter_id).first()
    if not version:
        return jsonify({'error': 'Version not found'}), 404
    
    try:
        # Update chapter with version content
        chapter.title = version.title
        chapter.content = version.content
        chapter.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'title': version.title,
            'content': version.content
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Rollback to version error: {e}")
        return jsonify({'error': 'Failed to rollback to version'}), 500

def create_simple_diff(old_text, new_text):
    """Create a simple HTML diff view"""
    if old_text == new_text:
        return '<p class="text-muted">No changes detected</p>'
    
    old_lines = old_text.split('\n') if old_text else []
    new_lines = new_text.split('\n') if new_text else []
    
    diff_html = '<div class="diff-container">'
    
    max_lines = max(len(old_lines), len(new_lines))
    
    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ''
        new_line = new_lines[i] if i < len(new_lines) else ''
        
        if old_line == new_line:
            diff_html += f'<div class="diff-line unchanged">{old_line}</div>'
        else:
            if old_line:
                diff_html += f'<div class="diff-line removed">- {old_line}</div>'
            if new_line:
                diff_html += f'<div class="diff-line added">+ {new_line}</div>'
    
    diff_html += '</div>'
    
    diff_html += '''
    <style>
    .diff-container { font-family: monospace; }
    .diff-line { padding: 2px 8px; margin: 1px 0; }
    .diff-line.removed { background-color: #ffebee; color: #c62828; }
    .diff-line.added { background-color: #e8f5e8; color: #2e7d32; }
    .diff-line.unchanged { color: #666; }
    </style>
    '''
    
    return diff_html
    
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
@require_login
def ai_suggestions(project_id):
    user_id = current_user.id
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
@require_login
def ai_preview(project_id):
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get suggestions from request args (passed from editor)
    suggestions = request.args.get('suggestions', {})
    
    return render_template('ai_preview.html', project=project, suggestions=suggestions)

@editor_bp.route('/upload_pdf/<int:project_id>', methods=['POST'])
@require_login
def upload_pdf(project_id):
    user_id = current_user.id
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
@require_login
def update_status(project_id):
    user_id = current_user.id
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    new_status = request.json.get('status') if request.json else None
    
    if new_status not in ['draft', 'in_progress', 'completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        project.status = new_status
        db.session.commit()
        
        status_display = new_status.replace("_", " ").title() if new_status else "Unknown"
        return jsonify({
            'success': True,
            'message': f'Project status updated to {status_display}'
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Status update error: {e}")
        return jsonify({'error': 'Failed to update status'}), 500
