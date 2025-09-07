#!/usr/bin/env python3
"""
Fix user passwords in database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from flask_security.utils import hash_password

def fix_passwords():
    with app.app_context():
        print("🔧 FIXING USER PASSWORDS")
        print("=" * 50)
        
        # Get admin user
        admin_user = User.query.filter_by(email='admin@mysticecho.com').first()
        if admin_user:
            print(f"Fixing admin user: {admin_user.email}")
            admin_user.password = hash_password('admin123')
            print("✅ Admin password set to 'admin123'")
        else:
            print("❌ Admin user not found!")
        
        # Get test user
        test_user = User.query.filter_by(email='test@mysticecho.com').first()
        if test_user:
            print(f"Fixing test user: {test_user.email}")
            test_user.password = hash_password('test123')
            print("✅ Test password set to 'test123'")
        else:
            print("❌ Test user not found!")
        
        # Commit changes
        try:
            db.session.commit()
            print("\n✅ Passwords updated successfully!")
        except Exception as e:
            print(f"\n❌ Error updating passwords: {e}")
            db.session.rollback()
        
        # Verify the passwords
        print("\n🔍 Verifying passwords...")
        from flask_security.utils import verify_password
        
        if admin_user:
            admin_valid = verify_password('admin123', admin_user.password)
            print(f"Admin 'admin123' valid: {admin_valid}")
        
        if test_user:
            test_valid = verify_password('test123', test_user.password)
            print(f"Test 'test123' valid: {test_valid}")

if __name__ == "__main__":
    fix_passwords()
