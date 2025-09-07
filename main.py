import logging
from app import app, db
from flask_security import auth_required, current_user
from flask import render_template, redirect, url_for, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Root route
@app.route('/')
def index():
    user = current_user
    logging.info(f"Index route - User authenticated: {user.is_authenticated}")
    logging.info(f"Index route - User email: {user.email if user.is_authenticated else 'N/A'}")
    if user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return render_template('landing.html')

# Debug route to check authentication state
@app.route('/debug-auth')
def debug_auth():
    fst_user = current_user
    
    return f"""
    <h1>Authentication Debug</h1>
    <h2>Flask-Security-Too current_user:</h2>
    <p>User authenticated: {fst_user.is_authenticated}</p>
    <p>User email: {fst_user.email if fst_user.is_authenticated else 'N/A'}</p>
    <p>User ID: {fst_user.id if fst_user.is_authenticated else 'N/A'}</p>
    <p>User active: {fst_user.active if fst_user.is_authenticated else 'N/A'}</p>
    <p>User confirmed_at: {fst_user.confirmed_at if fst_user.is_authenticated else 'N/A'}</p>
    <p>User fs_uniquifier: {fst_user.fs_uniquifier if fst_user.is_authenticated else 'N/A'}</p>
    
    <h2>Session Data:</h2>
    <p>Session keys: {list(session.keys())}</p>
    <p>Session data: {dict(session)}</p>
    
    <p><a href="/dashboard/">Try Dashboard</a></p>
    <p><a href="/logout">Logout</a></p>
    """

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

# Temporarily disable audio blueprint to fix hanging issue
logging.info("Audio blueprint temporarily disabled to fix hanging issue")

if __name__ == "__main__":
    print("🚀 Starting MysticEcho application...")
    print("🌐 Application will be available at: http://localhost:9001")
    print("🔐 Test accounts:")
    print("   Admin: admin@mysticecho.com / admin123")
    print("   User:  test@mysticecho.com / test123")
    print("")
    app.run(host="0.0.0.0", port=9001, debug=True)