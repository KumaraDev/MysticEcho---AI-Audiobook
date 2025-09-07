#!/usr/bin/env python3
"""
Create basic database tables and test users without Flask-Security-Too relationships
"""
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from flask_security import hash_password

def create_basic_tables():
    """Create basic database tables and test users"""
    
    with app.app_context():
        print("🗑️  Dropping all existing tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables...")
        db.create_all()
        
        print("📋 Checking created tables...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables created: {tables}")
        
        print("👤 Creating admin user directly in database...")
        try:
            # Create admin user directly in database
            with db.engine.connect() as conn:
                # Check if admin user already exists
                result = conn.execute(db.text("SELECT id FROM users WHERE email = 'admin@mysticecho.com'"))
                admin_row = result.fetchone()
                
                if admin_row:
                    admin_id = admin_row[0]
                    print(f"✅ Admin user already exists with ID: {admin_id}")
                else:
                    # Insert admin user
                    conn.execute(db.text("""
                        INSERT INTO users (email, password, active, fs_uniquifier, confirmed_at, first_name, last_name, created_at, updated_at)
                        VALUES (:email, :password, :active, :fs_uniquifier, :confirmed_at, :first_name, :last_name, :created_at, :updated_at)
                    """), {
                        'email': 'admin@mysticecho.com',
                        'password': hash_password('admin123'),
                        'active': True,
                        'fs_uniquifier': 'admin-unique-123',
                        'confirmed_at': datetime.now(),
                        'first_name': 'Admin',
                        'last_name': 'User',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    
                    # Get the admin user ID
                    result = conn.execute(db.text("SELECT id FROM users WHERE email = 'admin@mysticecho.com'"))
                    admin_id = result.fetchone()[0]
                    
                    print(f"✅ Admin user created with ID: {admin_id}")
                
                # Check if test user already exists
                result = conn.execute(db.text("SELECT id FROM users WHERE email = 'test@mysticecho.com'"))
                test_row = result.fetchone()
                
                if test_row:
                    print("✅ Test user already exists")
                else:
                    # Insert test user
                    conn.execute(db.text("""
                        INSERT INTO users (email, password, active, fs_uniquifier, confirmed_at, first_name, last_name, created_at, updated_at)
                        VALUES (:email, :password, :active, :fs_uniquifier, :confirmed_at, :first_name, :last_name, :created_at, :updated_at)
                    """), {
                        'email': 'test@mysticecho.com',
                        'password': hash_password('test123'),
                        'active': True,
                        'fs_uniquifier': 'test-unique-123',
                        'confirmed_at': datetime.now(),
                        'first_name': 'Test',
                        'last_name': 'User',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    
                    print("✅ Test user created")
                
                # Check if sample project already exists
                result = conn.execute(db.text("SELECT id FROM projects WHERE title = 'Sample Audiobook Project'"))
                project_row = result.fetchone()
                
                if project_row:
                    print("✅ Sample project already exists")
                else:
                    # Create sample project
                    conn.execute(db.text("""
                        INSERT INTO projects (title, description, content, user_id, status, created_at, updated_at)
                        VALUES (:title, :description, :content, :user_id, :status, :created_at, :updated_at)
                    """), {
                        'title': 'Sample Audiobook Project',
                        'description': 'This is a sample project to demonstrate the MysticEcho functionality.',
                        'content': 'Welcome to MysticEcho! This is your first audiobook project. You can start writing your content here and use the AI features to enhance your text.',
                        'user_id': admin_id,
                        'status': 'draft',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    
                    print("✅ Sample project created")
                
                conn.commit()
                
        except Exception as e:
            print(f"❌ Error creating users and project: {e}")
            return False
        
        print("✅ Database setup completed successfully!")
        print(f"   Admin user: admin@mysticecho.com / admin123")
        print(f"   Test user: test@mysticecho.com / test123")
        print(f"   Sample project created for admin user")
        return True

if __name__ == '__main__':
    success = create_basic_tables()
    if success:
        print("\n🎉 Ready to run the application!")
        print("Run: python3 main.py")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
