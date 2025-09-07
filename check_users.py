#!/usr/bin/env python3
"""
Check users in database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role
from flask_security.utils import hash_password

def check_users():
    with app.app_context():
        print("🔍 CHECKING USERS IN DATABASE")
        print("=" * 50)
        
        # Check all users
        users = User.query.all()
        print(f"\nFound {len(users)} users:")
        
        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Active: {user.active}")
            print(f"Confirmed at: {user.confirmed_at}")
            print(f"FS Uniquifier: {user.fs_uniquifier}")
            print(f"Password hash: {user.password[:50]}...")
            
            # Test password verification
            try:
                from flask_security.utils import verify_password
                is_valid = verify_password('admin123', user.password)
                print(f"Password 'admin123' valid: {is_valid}")
            except Exception as e:
                print(f"Password verification error: {e}")
        
        # Check roles
        roles = Role.query.all()
        print(f"\nFound {len(roles)} roles:")
        for role in roles:
            print(f"Role: {role.name} - {role.description}")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(email='admin@mysticecho.com').first()
        if admin_user:
            print(f"\n✅ Admin user found: {admin_user.email}")
            print(f"Active: {admin_user.active}")
            print(f"Confirmed: {admin_user.confirmed_at is not None}")
        else:
            print("\n❌ Admin user not found!")

if __name__ == "__main__":
    check_users()
