#!/usr/bin/env python3
"""
Reset user passwords to ensure they work correctly
"""
import os
import logging
from datetime import datetime
from app import app, db
from flask_security import hash_password
import models

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def reset_user_passwords():
    with app.app_context():
        print("🔄 Resetting user passwords...")
        
        try:
            # Update admin user password
            admin_user = db.session.query(models.User).filter_by(email='admin@mysticecho.com').first()
            if admin_user:
                admin_user.password = hash_password('admin123')
                admin_user.active = True
                admin_user.confirmed_at = datetime.now()
                print("✅ Admin user password reset")
            else:
                print("❌ Admin user not found")
            
            # Update test user password
            test_user = db.session.query(models.User).filter_by(email='test@mysticecho.com').first()
            if test_user:
                test_user.password = hash_password('test123')
                test_user.active = True
                test_user.confirmed_at = datetime.now()
                print("✅ Test user password reset")
            else:
                print("❌ Test user not found")
            
            db.session.commit()
            
            print("✅ Password reset completed successfully!")
            print("   Admin user: admin@mysticecho.com / admin123")
            print("   Test user: test@mysticecho.com / test123")
            return True
                
        except Exception as e:
            print(f"❌ Error resetting passwords: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    if reset_user_passwords():
        print("\n🎉 Passwords reset successfully!")
    else:
        print("\n❌ Password reset failed!")
