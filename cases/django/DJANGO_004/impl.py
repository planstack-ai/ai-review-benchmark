from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UserNotificationService:
    """Service for handling user-related notifications and communications."""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.welcome_template = 'emails/welcome_email.html'
    
    def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to newly registered user."""
        try:
            subject = f"Welcome to {getattr(settings, 'SITE_NAME', 'Our Platform')}, {user.first_name or user.username}!"
            
            context = {
                'user': user,
                'site_name': getattr(settings, 'SITE_NAME', 'Our Platform'),
                'login_url': self._get_login_url(),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
            }
            
            html_message = render_to_string(self.welcome_template, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=self.from_email,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Welcome email sent successfully to user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to user {user.id}: {str(e)}")
            return False
    
    def send_profile_update_notification(self, user: User) -> bool:
        """Send notification when user updates their profile."""
        try:
            subject = "Profile Updated Successfully"
            
            context = {
                'user': user,
                'site_name': getattr(settings, 'SITE_NAME', 'Our Platform')
            }
            
            html_message = render_to_string('emails/profile_update.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=self.from_email,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send profile update notification to user {user.id}: {str(e)}")
            return False
    
    def _get_login_url(self) -> str:
        """Get the login URL for the platform."""
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        return f"{base_url}/login/"
    
    def _should_send_welcome_email(self, user: User) -> bool:
        """Check if welcome email should be sent to user."""
        return bool(user.email and user.is_active)


notification_service = UserNotificationService()


@receiver(post_save, sender=User)
def handle_user_save(sender, instance, **kwargs):
    """Handle user save events for notifications."""
    if notification_service._should_send_welcome_email(instance):
        notification_service.send_welcome_email(instance)