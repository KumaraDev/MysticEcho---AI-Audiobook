#!/usr/bin/env python3
"""
Recreate database with proper Flask-Security-Too structure
"""
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, Project
from flask_security import hash_password

def recreate_database():
    """Recreate the database with proper Flask-Security-Too structure"""
    
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables...")
        db.create_all()
        
        print("👤 Creating admin user...")
        # Create admin user using Flask-Security-Too's create_user method
        from app import user_datastore
        
        admin_user = user_datastore.create_user(
            email='admin@mysticecho.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        print("👤 Creating test user...")
        # Create test user using Flask-Security-Too's create_user method
        test_user = user_datastore.create_user(
            email='test@mysticecho.com',
            password='test123',
            first_name='Test',
            last_name='User'
        )
        
        print("💾 Committing users...")
        db.session.commit()
        
        print("📚 Creating sample project...")
        # Create a sample project
        sample_project = Project()
        sample_project.title = 'Sample Audiobook Project'
        sample_project.description = 'This is a sample project to demonstrate the MysticEcho functionality.'
        sample_project.content = 'Welcome to MysticEcho! This is your first audiobook project. You can start writing your content here and use the AI features to enhance your text.'
        sample_project.user_id = admin_user.id
        sample_project.status = 'draft'
        sample_project.created_at = datetime.now()
        sample_project.updated_at = datetime.now()
        
        db.session.add(sample_project)
        
        print("💾 Committing all changes...")
        db.session.commit()
        
        print("✅ Database recreated successfully!")
        print(f"   Admin user: admin@mysticecho.com / admin123")
        print(f"   Test user: test@mysticecho.com / test123")
        print(f"   Sample project created for admin user")

if __name__ == '__main__':
    recreate_database()