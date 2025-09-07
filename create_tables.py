#!/usr/bin/env python3
"""
Create database tables and test users for Flask-Security-Too
"""
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, Project
from flask_security import hash_password

def create_tables_and_users():
    """Create database tables and test users"""
    
    with app.app_context():
        print("🗑️  Dropping all existing tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables...")
        db.create_all()
        
        print("📋 Checking created tables...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables created: {tables}")
        
        print("👤 Creating admin user...")
        # Create admin user using Flask-Security-Too's create_user method
        from app import user_datastore
        
        try:
            admin_user = user_datastore.create_user(
                email='admin@mysticecho.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            print(f"✅ Admin user created: {admin_user.email}")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            return False
        
        print("👤 Creating test user...")
        try:
            test_user = user_datastore.create_user(
                email='test@mysticecho.com',
                password='test123',
                first_name='Test',
                last_name='User'
            )
            print(f"✅ Test user created: {test_user.email}")
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False
        
        print("💾 Committing users...")
        try:
            db.session.commit()
            print("✅ Users committed successfully")
        except Exception as e:
            print(f"❌ Error committing users: {e}")
            return False
        
        print("📚 Creating sample project...")
        try:
            sample_project = Project()
            sample_project.title = 'Sample Audiobook Project'
            sample_project.description = 'This is a sample project to demonstrate the MysticEcho functionality.'
            sample_project.content = 'Welcome to MysticEcho! This is your first audiobook project. You can start writing your content here and use the AI features to enhance your text.'
            sample_project.user_id = admin_user.id
            sample_project.status = 'draft'
            sample_project.created_at = datetime.now()
            sample_project.updated_at = datetime.now()
            
            db.session.add(sample_project)
            db.session.commit()
            print("✅ Sample project created successfully")
        except Exception as e:
            print(f"❌ Error creating sample project: {e}")
            return False
        
        print("✅ Database setup completed successfully!")
        print(f"   Admin user: admin@mysticecho.com / admin123")
        print(f"   Test user: test@mysticecho.com / test123")
        print(f"   Sample project created for admin user")
        return True

if __name__ == '__main__':
    success = create_tables_and_users()
    if success:
        print("\n🎉 Ready to run the application!")
        print("Run: python3 main.py")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
