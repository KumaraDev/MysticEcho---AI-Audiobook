import logging
from app import app, db
from flask_security import login_required
from flask_login import current_user
from flask import render_template, redirect, url_for, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Register authentication blueprints
from routes.auth_security import auth_security_bp
app.register_blueprint(auth_security_bp, url_prefix='/auth')

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Root route
@app.route('/')
def index():
    user = current_user
    if user.is_authenticated:
        return redirect(url_for('dashboard_home'))
    else:
        return render_template('landing.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard_home():
    from models import Project
    user = current_user
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

# Register blueprints
try:
    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    logging.info("Registered dashboard blueprint")
except Exception as e:
    logging.error(f"Error registering dashboard blueprint: {e}")

try:
    from routes.editor import editor_bp
    app.register_blueprint(editor_bp, url_prefix='/editor')
    logging.info("Registered editor blueprint")
except Exception as e:
    logging.error(f"Error registering editor blueprint: {e}")

try:
    from routes.audio import audio_bp
    app.register_blueprint(audio_bp, url_prefix='/audio')
    logging.info("Registered audio blueprint")
except Exception as e:
    logging.error(f"Error registering audio blueprint: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)