import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Session configuration for better reliability
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.permanent_session_lifetime = 86400  # 24 hours

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mystic_echo.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")

# Register blueprints
from routes.auth import auth_bp
from routes.editor import editor_bp
from routes.dashboard import dashboard_bp
from routes.audio import audio_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(editor_bp, url_prefix='/editor')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(audio_bp, url_prefix='/audio')

# Root route
@app.route('/')
def index():
    from flask import session, redirect, url_for, render_template
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('landing.html')
