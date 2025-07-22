from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from models import Project, User
from app import db
import os
import tempfile
import logging

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')

def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@audio_bp.route('/generate/<int:project_id>')
@login_required
def generate_audio(project_id):
    """Show audio generation interface"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
        
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('dashboard.index'))
        
        return render_template('audio/generate.html', project=project)
        
    except Exception as e:
        logging.error(f"Error loading audio generation page: {e}")
        flash('Error loading audio generation page', 'error')
        return redirect(url_for('dashboard.index'))

@audio_bp.route('/generate_tts/<int:project_id>', methods=['POST'])
@login_required
def generate_tts(project_id):
    """Generate text-to-speech audio from project content"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'})
        
        data = request.get_json()
        text_to_convert = data.get('text', project.content)
        voice_settings = data.get('voice_settings', {})
        
        # For now, return a placeholder response
        # In a real implementation, you would:
        # 1. Use a TTS service like OpenAI TTS, ElevenLabs, or AWS Polly
        # 2. Split text into manageable chunks
        # 3. Generate audio files
        # 4. Store them in cloud storage
        
        return jsonify({
            'success': True,
            'message': 'Audio generation feature will be implemented with TTS service integration',
            'audio_url': None,
            'duration': 0,
            'file_size': 0
        })
        
    except Exception as e:
        logging.error(f"Error generating audio: {e}")
        return jsonify({'success': False, 'error': 'Failed to generate audio'})

@audio_bp.route('/chapters/<int:project_id>')
@login_required
def manage_chapters(project_id):
    """Show chapter management interface"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
        
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Split content into potential chapters (basic implementation)
        chapters = []
        if project.content:
            # Simple chapter detection based on headers or double line breaks
            content_parts = project.content.split('\n\n')
            for i, part in enumerate(content_parts):
                if part.strip():
                    chapters.append({
                        'number': i + 1,
                        'title': f'Chapter {i + 1}',
                        'content': part.strip()[:100] + '...' if len(part) > 100 else part.strip(),
                        'word_count': len(part.split())
                    })
        
        return render_template('audio/chapters.html', project=project, chapters=chapters)
        
    except Exception as e:
        logging.error(f"Error loading chapters page: {e}")
        flash('Error loading chapters page', 'error')
        return redirect(url_for('dashboard.index'))

@audio_bp.route('/preview/<int:project_id>')
@login_required
def preview_audio(project_id):
    """Show audio preview interface"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
        
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('dashboard.index'))
        
        return render_template('audio/preview.html', project=project)
        
    except Exception as e:
        logging.error(f"Error loading audio preview page: {e}")
        flash('Error loading audio preview page', 'error')
        return redirect(url_for('dashboard.index'))

@audio_bp.route('/export/<int:project_id>')
@login_required
def export_audiobook(project_id):
    """Show export/download interface"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))
        
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('dashboard.index'))
        
        return render_template('audio/export.html', project=project)
        
    except Exception as e:
        logging.error(f"Error loading export page: {e}")
        flash('Error loading export page', 'error')
        return redirect(url_for('dashboard.index'))

@audio_bp.route('/download/<int:project_id>')
@login_required
def download_audiobook(project_id):
    """Download the complete audiobook"""
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'})
        
        # Placeholder for actual download functionality
        return jsonify({
            'success': True,
            'message': 'Download feature will be implemented after audio generation is complete',
            'download_url': None
        })
        
    except Exception as e:
        logging.error(f"Error downloading audiobook: {e}")
        return jsonify({'success': False, 'error': 'Failed to download audiobook'})