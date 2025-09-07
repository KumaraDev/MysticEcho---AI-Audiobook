#!/usr/bin/env python3
"""
Fix database tables to use correct Flask-Security-Too table names
"""
import os
import logging
from datetime import datetime
from app import app, db
from flask_security import hash_password
import models  # Import models to ensure they are registered with SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def fix_database_tables():
    with app.app_context():
        print("🗑️  Dropping all existing tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables with correct structure...")
        db.create_all()
        
        print("📋 Checking created tables...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables created: {tables}")
        
        # Check if we have the correct table names
        if 'roles_users' in tables:
            print("✅ roles_users table found - correct!")
        elif 'user_roles' in tables:
            print("❌ user_roles table found - need to rename to roles_users")
            # Rename the table
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE user_roles RENAME TO roles_users"))
                conn.commit()
            print("✅ Renamed user_roles to roles_users")
        else:
            print("❌ No roles association table found")

        print("👤 Creating admin user...")
        try:
            import secrets
            
            # Check if admin user already exists
            admin_user = db.session.query(models.User).filter_by(email='admin@mysticecho.com').first()
            if not admin_user:
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
                print("✅ Admin user created")
            else:
                print("✅ Admin user already exists")
            
            # Check if test user already exists
            test_user = db.session.query(models.User).filter_by(email='test@mysticecho.com').first()
            if not test_user:
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
                print("✅ Test user created")
            else:
                print("✅ Test user already exists")
            
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
    if fix_database_tables():
        print("\n🎉 Ready to run the application!")
        print("Run: python3 main.py")
    else:
        print("\n❌ Database setup failed!")
