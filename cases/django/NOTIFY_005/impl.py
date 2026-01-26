from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OrderNotificationService:
    """Service for handling order-related email notifications."""
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.admin_email = settings.ADMIN_EMAIL
    
    def send_order_confirmation(self, order) -> bool:
        """Send order confirmation email to customer."""
        try:
            subject = f"Order Confirmation #{order.order_number}"
            message = self._build_confirmation_message(order)
            
            return self._send_notification_email(
                subject=subject,
                message=message,
                recipient_email=order.user.email
            )
        except Exception as e:
            logger.error(f"Failed to send order confirmation: {e}")
            return False
    
    def send_order_status_update(self, order, status_change: str) -> bool:
        """Send order status update notification."""
        try:
            subject = f"Order Update #{order.order_number}"
            message = self._build_status_update_message(order, status_change)
            
            return self._send_notification_email(
                subject=subject,
                message=message,
                recipient_email=order.user.email
            )
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
            return False
    
    def send_payment_reminder(self, order) -> bool:
        """Send payment reminder for pending orders."""
        if order.status != 'pending_payment':
            return False
        
        try:
            user = order.user
            admin_user = self._get_admin_user()
            
            subject = f"Payment Reminder - Order #{order.order_number}"
            message = self._build_payment_reminder_message(order)
            
            success = self._send_notification_email(
                subject=subject,
                message=message,
                recipient_email=user.email
            )
            
            if success:
                self._log_reminder_sent(order, admin_user)
            
            return success
        except Exception as e:
            logger.error(f"Failed to send payment reminder: {e}")
            return False
    
    def _build_confirmation_message(self, order) -> str:
        """Build order confirmation email message."""
        total = order.total_amount
        items_count = order.items.count()
        
        return f"""
        Dear {order.user.first_name},
        
        Thank you for your order! Your order #{order.order_number} has been confirmed.
        
        Order Details:
        - Items: {items_count}
        - Total: ${total}
        - Estimated delivery: {order.estimated_delivery_date}
        
        We'll send you updates as your order progresses.
        
        Best regards,
        The Team
        """
    
    def _build_status_update_message(self, order, status_change: str) -> str:
        """Build status update email message."""
        return f"""
        Dear {order.user.first_name},
        
        Your order #{order.order_number} status has been updated to: {status_change}
        
        You can track your order at any time in your account dashboard.
        
        Best regards,
        The Team
        """
    
    def _build_payment_reminder_message(self, order) -> str:
        """Build payment reminder email message."""
        return f"""
        Dear {order.user.first_name},
        
        This is a friendly reminder that payment is still pending for order #{order.order_number}.
        
        Order Total: ${order.total_amount}
        
        Please complete your payment to avoid order cancellation.
        
        Best regards,
        The Team
        """
    
    def _send_notification_email(self, subject: str, message: str, recipient_email: str) -> bool:
        """Send email notification."""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[recipient_email],
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _get_admin_user(self):
        """Get admin user for logging purposes."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(is_staff=True).first()
    
    def _log_reminder_sent(self, order, user) -> None:
        """Log that payment reminder was sent."""
        logger.info(f"Payment reminder sent for order {order.order_number} to {user.email}")