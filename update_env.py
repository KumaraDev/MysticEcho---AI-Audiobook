#!/usr/bin/env python3
"""
Script to update .env file with Flask-Security-Too configuration
"""
import os
import secrets
import string

def generate_random_salt():
    """Generate a random salt for password hashing"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def update_env_file():
    """Update .env file with Flask-Security-Too configuration"""
    env_file = '.env'
    
    # Read current .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Add Flask-Security-Too configuration if not present
    security_config = """
# Flask-Security-Too Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
SECURITY_PASSWORD_SALT={}
SECURITY_EMAIL_SENDER=your-email@gmail.com""".format(generate_random_salt())
    
    # Check if Flask-Security-Too config already exists
    if "Flask-Security-Too Configuration" not in content:
        # Add before Application URL section
        if "APP_BASE_URL=" in content:
            content = content.replace("# Application URL (Optional)\nAPP_BASE_URL=", 
                                    security_config + "\n\n# Application URL (Optional)\nAPP_BASE_URL=")
        else:
            content += security_config + "\n"
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated .env file with Flask-Security-Too configuration")
        print("🔑 Generated new SECURITY_PASSWORD_SALT")
        print("📧 Please update MAIL_USERNAME and MAIL_PASSWORD with your email credentials")
    else:
        print("✅ Flask-Security-Too configuration already exists in .env file")

if __name__ == "__main__":
    update_env_file()
