#!/usr/bin/env python3
"""
Recreate database with correct Flask-Security-Too table structure
"""
import os
import logging
from datetime import datetime
from app import app, db
from flask_security import hash_password
import models  # Import models to ensure they are registered with SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def recreate_database():
    with app.app_context():
        print("🗑️  Dropping all existing tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables with correct structure...")
        db.create_all()
        
        print("📋 Checking created tables...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables created: {tables}")

        print("👤 Creating admin user...")
        try:
            import secrets
            
            # Create admin user using Flask-Security-Too's create_user method
            admin_user = models.User(
                email='admin@mysticecho.com',
                password=hash_password('admin123'),
                active=True,
                confirmed_at=datetime.now(),
                fs_uniquifier=secrets.token_urlsafe(32),
                first_name='Admin',
                last_name='User'
            )
            db.session.add(admin_user)
            
            # Create test user
            test_user = models.User(
                email='test@mysticecho.com',
                password=hash_password('test123'),
                active=True,
                confirmed_at=datetime.now(),
                fs_uniquifier=secrets.token_urlsafe(32),
                first_name='Test',
                last_name='User'
            )
            db.session.add(test_user)
            
            # Commit users first
            db.session.commit()
            
            # Create sample project for admin user
            sample_project = models.Project(
                title='Sample Audiobook Project',
                description='This is a sample project to demonstrate the MysticEcho functionality.',
                content='Welcome to MysticEcho! This is your first audiobook project. You can start writing your content here and use the AI features to enhance your text.',
                user_id=admin_user.id,
                status='draft'
            )
            db.session.add(sample_project)
            
            db.session.commit()
            
            print("✅ Database setup completed successfully!")
            print("   Admin user: admin@mysticecho.com / admin123")
            print("   Test user: test@mysticecho.com / test123")
            print("   Sample project created for admin user")
            return True
                
        except Exception as e:
            print(f"❌ Error creating users and project: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    if recreate_database():
        print("\n🎉 Ready to run the application!")
        print("Run: python3 main.py")
    else:
        print("\n❌ Database setup failed!")
