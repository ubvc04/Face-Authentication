"""
Email service for sending OTP and login notifications.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('FROM_NAME', 'Face Auth App')
        
    def send_email(self, to_email: str, subject: str, html_body: str, 
                   text_body: str = "") -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (fallback)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_otp_email(self, to_email: str, otp: str, name: str) -> bool:
        """
        Send OTP verification email.
        
        Args:
            to_email: Recipient email address
            otp: 6-digit OTP code
            name: User's name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Verify Your Face Auth Account"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #2563eb; margin-bottom: 10px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #1f2937; background-color: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; letter-spacing: 5px; margin: 20px 0; }}
                .warning {{ color: #ef4444; font-size: 14px; margin-top: 20px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔐 Face Auth</div>
                    <h1>Verify Your Account</h1>
                </div>
                
                <p>Hello {name},</p>
                
                <p>Thank you for signing up for Face Auth! To complete your registration, please use the verification code below:</p>
                
                <div class="otp-code">{otp}</div>
                
                <p>This code will expire in 10 minutes for security reasons.</p>
                
                <p class="warning">⚠️ If you didn't create an account with Face Auth, please ignore this email.</p>
                
                <div class="footer">
                    <p>Face Auth - Secure Authentication System</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Face Auth - Account Verification
        
        Hello {name},
        
        Thank you for signing up for Face Auth! To complete your registration, please use this verification code:
        
        {otp}
        
        This code will expire in 10 minutes for security reasons.
        
        If you didn't create an account with Face Auth, please ignore this email.
        
        ---
        Face Auth - Secure Authentication System
        """
        
        return self.send_email(to_email, subject, html_body, text_body)
    
    def send_login_notification(self, to_email: str, name: str, 
                              login_time: Optional[datetime] = None) -> bool:
        """
        Send login notification email.
        
        Args:
            to_email: User's email address
            name: User's name
            login_time: Login timestamp (defaults to now)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if login_time is None:
            login_time = datetime.utcnow()
        
        formatted_time = login_time.strftime("%B %d, %Y at %I:%M %p UTC")
        
        subject = "Login Detected - Face Auth"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #10b981; margin-bottom: 10px; }}
                .login-info {{ background-color: #ecfdf5; padding: 20px; border-radius: 8px; border-left: 4px solid #10b981; margin: 20px 0; }}
                .warning {{ color: #f59e0b; font-size: 14px; margin-top: 20px; padding: 15px; background-color: #fffbeb; border-radius: 8px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🔐 Face Auth</div>
                    <h1>Login Detected</h1>
                </div>
                
                <p>Hello {name},</p>
                
                <p>We detected a successful login to your Face Auth account using face recognition.</p>
                
                <div class="login-info">
                    <strong>Login Details:</strong><br>
                    📅 Time: {formatted_time}<br>
                    🔐 Method: Face Recognition
                </div>
                
                <div class="warning">
                    ⚠️ If this wasn't you, please contact support immediately and consider changing your password.
                </div>
                
                <div class="footer">
                    <p>Face Auth - Secure Authentication System</p>
                    <p>This is an automated security notification.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Face Auth - Login Detected
        
        Hello {name},
        
        We detected a successful login to your Face Auth account using face recognition.
        
        Login Details:
        Time: {formatted_time}
        Method: Face Recognition
        
        If this wasn't you, please contact support immediately and consider changing your password.
        
        ---
        Face Auth - Secure Authentication System
        """
        
        return self.send_email(to_email, subject, html_body, text_body)

# Global instance
email_service = EmailService()