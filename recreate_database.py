#!/usr/bin/env python3
"""
Recreate Database Script for Flask-Security-Too Integration
Creates a fresh database with the correct schema
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, user_roles, Project, ProjectVersion, Chapter
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
import uuid

def recreate_database():
    """Recreate database with correct schema"""
    with app.app_context():
        print("🔄 Recreating database with Flask-Security-Too schema...")
        
        # Drop all tables
        db.drop_all()
        print("✅ Dropped all existing tables")
        
        # Create all tables with new schema
        db.create_all()
        print("✅ Created all tables with new schema")
        
        # Initialize user datastore
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        
        # Create roles
        admin_role = user_datastore.create_role(name='admin', description='Administrator')
        user_role = user_datastore.create_role(name='user', description='Regular User')
        print("✅ Created roles")
        
        # Create admin user
        admin_user = user_datastore.create_user(
            email='admin@mysticecho.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            confirmed_at=datetime.now(),
            fs_uniquifier=str(uuid.uuid4())
        )
        
        # Assign admin role
        user_datastore.add_role_to_user(admin_user, admin_role)
        print("✅ Created admin user")
        
        # Create test user
        test_user = user_datastore.create_user(
            email='test@mysticecho.com',
            password='test123',
            first_name='Test',
            last_name='User',
            confirmed_at=datetime.now(),
            fs_uniquifier=str(uuid.uuid4())
        )
        
        # Assign user role
        user_datastore.add_role_to_user(test_user, user_role)
        print("✅ Created test user")
        
        # Flush to get user IDs
        db.session.flush()
        
        # Create a sample project
        sample_project = Project(
            title='Sample Audiobook Project',
            description='A sample project to test the application',
            content='This is a sample project content. It will be used to test the audiobook generation features.',
            user_id=test_user.id,
            status='draft'
        )
        db.session.add(sample_project)
        print("✅ Created sample project")
        
        # Commit all changes
        db.session.commit()
        print("✅ Database recreation completed successfully!")
        
        print("\n🎉 Database setup complete!")
        print("📋 Test accounts created:")
        print("   Admin: admin@mysticecho.com / admin123")
        print("   User:  test@mysticecho.com / test123")
        print("   Sample project created for test user")

def main():
    """Main function"""
    print("🚀 MysticEcho Database Recreation Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the MysticEcho directory.")
        return
    
    try:
        recreate_database()
    except Exception as e:
        print(f"❌ Database recreation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
