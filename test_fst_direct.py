#!/usr/bin/env python3
"""
Direct Flask-Security-Too test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, user_datastore
from models import User
from flask_security.utils import hash_password, verify_password

def test_fst_direct():
    with app.app_context():
        print("🔍 DIRECT FLASK-SECURITY-TOO TEST")
        print("=" * 50)
        
        # Test user lookup
        admin_user = user_datastore.find_user(email='admin@mysticecho.com')
        if admin_user:
            print(f"✅ Admin user found: {admin_user.email}")
            print(f"Active: {admin_user.active}")
            print(f"Confirmed: {admin_user.confirmed_at is not None}")
            
            # Test password verification
            is_valid = verify_password('admin123', admin_user.password)
            print(f"Password valid: {is_valid}")
            
            # Test user authentication
            print(f"User ID: {admin_user.get_id()}")
            print(f"User roles: {[role.name for role in admin_user.roles]}")
            
        else:
            print("❌ Admin user not found!")
        
        # Test datastore methods
        print(f"\nDatastore methods:")
        print(f"find_user: {hasattr(user_datastore, 'find_user')}")
        print(f"authenticate_user: {hasattr(user_datastore, 'authenticate_user')}")
        
        # Test authentication
        if admin_user:
            try:
                auth_result = user_datastore.authenticate_user(admin_user, 'admin123')
                print(f"Authentication result: {auth_result}")
            except Exception as e:
                print(f"Authentication error: {e}")

if __name__ == "__main__":
    test_fst_direct()
