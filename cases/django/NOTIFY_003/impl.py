from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Order, Payment, OrderItem
from .exceptions import OrderProcessingError, PaymentError


class OrderProcessingService:
    """Service for handling order creation and payment processing workflow."""
    
    def __init__(self):
        self.payment_gateway = self._get_payment_gateway()
    
    def create_order(self, user: User, items: list, shipping_address: Dict[str, str]) -> Order:
        """Create a new order with items and initiate payment processing."""
        with transaction.atomic():
            order = self._create_order_instance(user, shipping_address)
            self._add_items_to_order(order, items)
            order.total_amount = self._calculate_total(order)
            order.save()
            
            self._send_order_confirmation(order)
            self._initiate_payment_processing(order)
            
            return order
    
    def process_payment_callback(self, payment_id: str, status: str, transaction_data: Dict[str, Any]) -> bool:
        """Handle payment gateway callback and update payment status."""
        try:
            payment = Payment.objects.get(external_id=payment_id)
            payment.status = status
            payment.transaction_data = transaction_data
            payment.processed_at = timezone.now()
            payment.save()
            
            if status == 'completed':
                self._handle_successful_payment(payment)
            elif status == 'failed':
                self._handle_failed_payment(payment)
                
            return True
        except Payment.DoesNotExist:
            raise PaymentError(f"Payment with ID {payment_id} not found")
    
    def _create_order_instance(self, user: User, shipping_address: Dict[str, str]) -> Order:
        """Create the base order instance with user and shipping details."""
        return Order.objects.create(
            user=user,
            status='pending',
            shipping_address=shipping_address,
            created_at=timezone.now()
        )
    
    def _add_items_to_order(self, order: Order, items: list) -> None:
        """Add items to the order and validate inventory."""
        for item_data in items:
            OrderItem.objects.create(
                order=order,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['price']
            )
    
    def _calculate_total(self, order: Order) -> Decimal:
        """Calculate the total amount for the order including tax and shipping."""
        subtotal = sum(item.quantity * item.unit_price for item in order.items.all())
        tax = subtotal * Decimal('0.08')
        shipping = Decimal('9.99') if subtotal < Decimal('50.00') else Decimal('0.00')
        return subtotal + tax + shipping
    
    def _send_order_confirmation(self, order: Order) -> None:
        """Send order confirmation email to customer."""
        subject = f'Order Confirmation #{order.id}'
        message = f'Thank you for your order! Your order #{order.id} has been confirmed and payment has been processed successfully.'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False
        )
    
    def _initiate_payment_processing(self, order: Order) -> Payment:
        """Create payment record and initiate processing with payment gateway."""
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            status='pending',
            created_at=timezone.now()
        )
        
        gateway_response = self.payment_gateway.process_payment(
            amount=order.total_amount,
            order_id=order.id,
            customer_email=order.user.email
        )
        
        payment.external_id = gateway_response.get('transaction_id')
        payment.save()
        
        return payment
    
    def _handle_successful_payment(self, payment: Payment) -> None:
        """Process successful payment and update order status."""
        order = payment.order
        order.status = 'confirmed'
        order.payment_confirmed_at = timezone.now()
        order.save()
    
    def _handle_failed_payment(self, payment: Payment) -> None:
        """Handle failed payment and update order accordingly."""
        order = payment.order
        order.status = 'payment_failed'
        order.save()
    
    def _get_payment_gateway(self):
        """Initialize and return payment gateway instance."""
        from .payment_gateways import PaymentGatewayFactory
        return PaymentGatewayFactory.create_gateway(settings.PAYMENT_GATEWAY_TYPE)