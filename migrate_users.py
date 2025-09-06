#!/usr/bin/env python3
"""
User Migration Script for Flask-Security-Too Integration
Migrates existing Replit OAuth users to Flask-Security-Too format
"""
import os
import sys
import secrets
import string
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, user_roles
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

def generate_random_password():
    """Generate a random password for migrated users"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

def migrate_users():
    """Migrate existing users to Flask-Security-Too format"""
    with app.app_context():
        print("🔄 Starting user migration...")
        
        # Initialize user datastore
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        
        # Create roles if they don't exist
        admin_role = user_datastore.find_role('admin')
        if not admin_role:
            admin_role = user_datastore.create_role(name='admin', description='Administrator')
            print("✅ Created admin role")
        
        user_role = user_datastore.find_role('user')
        if not user_role:
            user_role = user_datastore.create_role(name='user', description='Regular User')
            print("✅ Created user role")
        
        # Get existing users (from old format)
        existing_users = User.query.filter(User.password_hash.is_(None)).all()
        
        if not existing_users:
            print("ℹ️  No users found that need migration")
            return
        
        print(f"📊 Found {len(existing_users)} users to migrate")
        
        # Migrate each user
        for user in existing_users:
            try:
                # Generate temporary password
                temp_password = generate_random_password()
                
                # Set password hash
                user.password_hash = hash_password(temp_password)
                
                # Set confirmed_at to created_at (auto-confirm existing users)
                user.confirmed_at = user.created_at or datetime.now()
                
                # Assign user role
                user.roles.append(user_role)
                
                # Update email if it's None (some users might not have email)
                if not user.email:
                    user.email = f"user_{user.id}@migrated.local"
                    print(f"⚠️  User {user.id} had no email, assigned temporary email: {user.email}")
                
                print(f"✅ Migrated user: {user.email} (ID: {user.id})")
                print(f"   Temporary password: {temp_password}")
                print(f"   Please change password on first login")
                print()
                
            except Exception as e:
                print(f"❌ Error migrating user {user.id}: {e}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print("✅ Migration completed successfully!")
            print(f"📧 {len(existing_users)} users migrated")
            print("🔑 All users have temporary passwords - they should change them on first login")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            return False
        
        return True

def create_admin_user():
    """Create an admin user for testing"""
    with app.app_context():
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        
        # Check if admin user already exists
        admin_user = user_datastore.find_user(email='admin@mysticecho.com')
        if admin_user:
            print("ℹ️  Admin user already exists")
            return
        
        # Create admin user
        admin_password = 'admin123'  # Change this in production!
        admin_user = user_datastore.create_user(
            email='admin@mysticecho.com',
            password=admin_password,
            first_name='Admin',
            last_name='User',
            confirmed_at=datetime.now()
        )
        
        # Assign admin role
        admin_role = user_datastore.find_role('admin')
        if admin_role:
            user_datastore.add_role_to_user(admin_user, admin_role)
        
        db.session.commit()
        print("✅ Created admin user: admin@mysticecho.com")
        print(f"🔑 Admin password: {admin_password}")

def main():
    """Main migration function"""
    print("🚀 MysticEcho User Migration Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the MysticEcho directory.")
        return
    
    try:
        # Run migration
        success = migrate_users()
        
        if success:
            # Create admin user
            create_admin_user()
            
            print("\n🎉 Migration completed successfully!")
            print("📋 Next steps:")
            print("1. Update your .env file with email credentials")
            print("2. Test the application with migrated users")
            print("3. Remove old OAuth system when ready")
            
        else:
            print("\n❌ Migration failed. Please check the errors above.")
            
    except Exception as e:
        print(f"❌ Migration script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
