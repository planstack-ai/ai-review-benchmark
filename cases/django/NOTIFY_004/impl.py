from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for handling email notifications with template rendering."""
    
    def __init__(self):
        self.default_from_email = settings.DEFAULT_FROM_EMAIL
        self.template_context = {}
    
    def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to newly registered user."""
        try:
            context = self._build_welcome_context(user)
            return self._send_templated_email(
                template_name='emails/welcome.html',
                subject='Welcome to Our Platform!',
                recipient_email=user.email,
                context=context
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False
    
    def send_password_reset_email(self, user: User, reset_token: str) -> bool:
        """Send password reset email with secure token."""
        try:
            context = self._build_reset_context(user, reset_token)
            return self._send_templated_email(
                template_name='emails/password_reset.html',
                subject='Password Reset Request',
                recipient_email=user.email,
                context=context
            )
        except Exception as e:
            logger.error(f"Failed to send reset email to {user.email}: {str(e)}")
            return False
    
    def send_account_verification_email(self, user: User, verification_code: str) -> bool:
        """Send account verification email with confirmation code."""
        try:
            context = self._build_verification_context(user, verification_code)
            return self._send_templated_email(
                template_name='emails/account_verification.html',
                subject='Please Verify Your Account',
                recipient_email=user.email,
                context=context
            )
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False
    
    def _build_welcome_context(self, user: User) -> Dict[str, Any]:
        """Build context dictionary for welcome email template."""
        return {
            'user': user,
            'user_name': user.name,
            'platform_name': 'CodeReview Pro',
            'support_email': settings.SUPPORT_EMAIL,
            'login_url': f"{settings.SITE_URL}/login/"
        }
    
    def _build_reset_context(self, user: User, reset_token: str) -> Dict[str, Any]:
        """Build context dictionary for password reset email template."""
        return {
            'user': user,
            'user_name': user.name,
            'reset_token': reset_token,
            'reset_url': f"{settings.SITE_URL}/reset-password/{reset_token}/",
            'expiry_hours': 24
        }
    
    def _build_verification_context(self, user: User, verification_code: str) -> Dict[str, Any]:
        """Build context dictionary for verification email template."""
        return {
            'user': user,
            'user_name': user.name,
            'verification_code': verification_code,
            'verification_url': f"{settings.SITE_URL}/verify/{verification_code}/",
            'platform_name': 'CodeReview Pro'
        }
    
    def _send_templated_email(self, template_name: str, subject: str, 
                            recipient_email: str, context: Dict[str, Any]) -> bool:
        """Send email using Django template rendering."""
        try:
            html_content = render_to_string(template_name, context)
            
            send_mail(
                subject=subject,
                message='',
                html_message=html_content,
                from_email=self.default_from_email,
                recipient_list=[recipient_email],
                fail_silently=False
            )
            
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False