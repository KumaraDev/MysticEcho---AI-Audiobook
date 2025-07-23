import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_password_reset_email(user_email, user_name, reset_token):
    """Send password reset email to user"""
    try:
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_key:
            logging.error("SendGrid API key not found")
            return False
        
        sg = SendGridAPIClient(sendgrid_key)
        
        # Create reset URL - using the domain from the request
        from flask import request
        reset_url = f"{request.url_root}auth/reset-password/{reset_token}"
        
        # Email content
        subject = "Password Reset - Mystic Echo"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎧 Mystic Echo</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Password Reset Request</h2>
                
                <p>Hello {user_name},</p>
                
                <p>You recently requested to reset your password for your Mystic Echo account. Click the button below to reset it:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    If the button doesn't work, you can copy and paste this link into your browser:
                    <br><a href="{reset_url}" style="color: #667eea;">{reset_url}</a>
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 1 hour for security reasons.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you didn't request this password reset, you can safely ignore this email.
                </p>
            </div>
            
            <div style="background: #e9ecef; padding: 20px; text-align: center; color: #666; font-size: 12px;">
                <p>© 2025 Mystic Echo - AI-Powered Audiobook Creation Platform</p>
            </div>
        </div>
        """
        
        text_content = f"""
        Password Reset - Mystic Echo
        
        Hello {user_name},
        
        You recently requested to reset your password for your Mystic Echo account.
        
        Please visit this link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, you can safely ignore this email.
        
        © 2025 Mystic Echo
        """
        
        message = Mail(
            from_email=Email("noreply@mysticecho.app", "Mystic Echo"),
            to_emails=To(user_email),
            subject=subject,
            html_content=Content("text/html", html_content),
            plain_text_content=Content("text/plain", text_content)
        )
        
        response = sg.send(message)
        logging.info(f"Password reset email sent to {user_email}, status: {response.status_code}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send password reset email: {e}")
        return False

def send_welcome_email(user_email, user_name):
    """Send welcome email to new users"""
    try:
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        if not sendgrid_key:
            return True  # Don't fail registration if email fails
        
        sg = SendGridAPIClient(sendgrid_key)
        
        subject = "Welcome to Mystic Echo!"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎧 Welcome to Mystic Echo!</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <h2 style="color: #333;">Your audiobook journey begins now</h2>
                
                <p>Hello {user_name},</p>
                
                <p>Welcome to Mystic Echo! We're excited to help you create amazing audiobooks with the power of AI.</p>
                
                <p>Here's what you can do:</p>
                <ul>
                    <li>📝 Create and edit manuscripts with our rich text editor</li>
                    <li>🤖 Get AI-powered content suggestions and improvements</li>
                    <li>📊 Organize your work with chapter management</li>
                    <li>🎙️ Convert your text to professional audio</li>
                    <li>📱 Export your finished audiobooks</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p>Ready to start creating? Log in to your account and begin your audiobook journey!</p>
                </div>
            </div>
            
            <div style="background: #e9ecef; padding: 20px; text-align: center; color: #666; font-size: 12px;">
                <p>© 2025 Mystic Echo - AI-Powered Audiobook Creation Platform</p>
            </div>
        </div>
        """
        
        message = Mail(
            from_email=Email("noreply@mysticecho.app", "Mystic Echo"),
            to_emails=To(user_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )
        
        response = sg.send(message)
        logging.info(f"Welcome email sent to {user_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send welcome email: {e}")
        return True  # Don't fail registration if email fails