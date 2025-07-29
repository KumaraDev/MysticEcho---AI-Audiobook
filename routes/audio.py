from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import Project, User
from app import db
from flask_login import current_user
from replit_auth import require_login
import os
import tempfile
import logging

audio_bp = Blueprint('audio', __name__, url_prefix='/audio')

@audio_bp.route('/generate/<int:project_id>')
@require_login
def generate_audio(project_id):
    """Show audio generation interface"""
    try:
        user = current_user
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
@require_login
def generate_tts(project_id):
    """Generate text-to-speech audio from project content"""
    try:
        user = current_user
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'})
        
        # Get the text content to convert
        content = project.content
        if not content or not content.strip():
            return jsonify({'success': False, 'error': 'No content to convert'})
        
        # Update project status to generating_audio
        project.status = 'generating_audio'
        db.session.commit()
        
        # Here you would integrate with OpenAI TTS API
        # For now, we'll return a placeholder response
        return jsonify({
            'success': True,
            'message': 'Audio generation started',
            'audio_url': None  # Will be populated when actual TTS is implemented
        })
        
    except Exception as e:
        logging.error(f"TTS generation error: {e}")
        return jsonify({'success': False, 'error': 'Failed to generate audio'})

@audio_bp.route('/preview/<int:project_id>')
@require_login
def preview_audio(project_id):
    """Preview generated audio"""
    try:
        user = current_user
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('audio/preview.html', project=project)
        
    except Exception as e:
        logging.error(f"Error loading audio preview: {e}")
        flash('Error loading audio preview', 'error')
        return redirect(url_for('dashboard'))

@audio_bp.route('/download/<int:project_id>')
@require_login
def download_audio(project_id):
    """Download generated audio file"""
    try:
        user = current_user
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'})
        
        # Here you would implement the actual file download
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'download_url': f'/downloads/audiobook_{project_id}.mp3'
        })
        
    except Exception as e:
        logging.error(f"Audio download error: {e}")
        return jsonify({'success': False, 'error': 'Failed to download audio'})

@audio_bp.route('/export/<int:project_id>')
@require_login
def export_audiobook(project_id):
    """Export audiobook in various formats"""
    try:
        user = current_user
        project = Project.query.filter_by(id=project_id, user_id=user.id).first()
        
        if not project:
            flash('Project not found', 'error')
            return redirect(url_for('dashboard'))
        
        return render_template('audio/export.html', project=project)
        
    except Exception as e:
        logging.error(f"Error loading export page: {e}")
        flash('Error loading export page', 'error')
        return redirect(url_for('dashboard'))