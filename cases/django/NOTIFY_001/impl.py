from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from orders.models import Order
from products.models import Product
import logging

logger = logging.getLogger(__name__)


class OrderConfirmationService:
    """Service for handling order confirmation processes including email notifications."""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
    
    def process_order_confirmation(self, order_id: int) -> bool:
        """Process complete order confirmation workflow with retry logic."""
        try:
            order = Order.objects.select_related('customer').get(id=order_id)
            
            if not self._validate_order_for_confirmation(order):
                logger.warning(f"Order {order_id} failed validation for confirmation")
                return False
            
            with transaction.atomic():
                self._update_order_status(order)
                success = self._send_confirmation_email_with_retry(order)
                
                if success:
                    order.confirmation_processed_at = timezone.now()
                    order.save(update_fields=['confirmation_processed_at'])
                    logger.info(f"Order confirmation completed for order {order_id}")
                    return True
                
            return False
            
        except Order.DoesNotExist:
            logger.error(f"Order {order_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error processing order confirmation {order_id}: {str(e)}")
            return False
    
    def _validate_order_for_confirmation(self, order: Order) -> bool:
        """Validate order is ready for confirmation email."""
        if order.status != 'completed':
            return False
        
        if not order.customer or not order.customer.email:
            return False
        
        if order.total_amount <= Decimal('0.00'):
            return False
        
        return True
    
    def _update_order_status(self, order: Order) -> None:
        """Update order status and related fields."""
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save(update_fields=['status', 'confirmed_at'])
    
    def _send_confirmation_email_with_retry(self, order: Order) -> bool:
        """Send confirmation email with retry mechanism."""
        for attempt in range(self.max_retries):
            try:
                if self._send_confirmation_email(order):
                    return True
                    
                logger.warning(f"Email send attempt {attempt + 1} failed for order {order.id}")
                
            except Exception as e:
                logger.error(f"Email send error on attempt {attempt + 1} for order {order.id}: {str(e)}")
        
        logger.error(f"Failed to send confirmation email after {self.max_retries} attempts for order {order.id}")
        return False
    
    def _send_confirmation_email(self, order: Order) -> bool:
        """Send the actual confirmation email."""
        try:
            context = self._build_email_context(order)
            
            html_content = render_to_string('emails/order_confirmation.html', context)
            text_content = render_to_string('emails/order_confirmation.txt', context)
            
            send_mail(
                subject=f'Order Confirmation #{order.order_number}',
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.customer.email],
                html_message=html_content,
                fail_silently=False
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email for order {order.id}: {str(e)}")
            return False
    
    def _build_email_context(self, order: Order) -> Dict[str, Any]:
        """Build context dictionary for email templates."""
        return {
            'order': order,
            'customer': order.customer,
            'order_items': order.items.select_related('product').all(),
            'total_amount': order.total_amount,
            'order_date': order.created_at,
            'company_name': getattr(settings, 'COMPANY_NAME', 'Our Store'),
        }