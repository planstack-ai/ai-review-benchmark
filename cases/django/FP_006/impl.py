from decimal import Decimal
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from myapp.models import Order, OrderItem, Product, Inventory, PaymentTransaction


class OrderProcessingService:
    
    def process_order(self, order_id: int, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction.atomic():
            order = self._get_and_validate_order(order_id)
            self._validate_inventory_availability(order)
            
            payment_result = self._process_payment_with_nested_transaction(order, payment_data)
            
            if payment_result['success']:
                self._update_inventory_levels(order)
                self._finalize_order_status(order)
                return {
                    'success': True,
                    'order_id': order.id,
                    'payment_id': payment_result['payment_id'],
                    'total_amount': order.total_amount
                }
            else:
                raise ValidationError("Payment processing failed")
    
    def _get_and_validate_order(self, order_id: int) -> Order:
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            raise ValidationError(f"Order {order_id} not found")
        
        if order.status != 'pending':
            raise ValidationError(f"Order {order_id} is not in pending status")
        
        return order
    
    def _validate_inventory_availability(self, order: Order) -> None:
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        
        for item in order_items:
            inventory = Inventory.objects.select_for_update().get(product=item.product)
            if inventory.available_quantity < item.quantity:
                raise ValidationError(
                    f"Insufficient inventory for product {item.product.name}"
                )
    
    def _process_payment_with_nested_transaction(self, order: Order, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        with transaction.atomic():
            payment_transaction = PaymentTransaction.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method=payment_data['method'],
                status='processing',
                created_at=timezone.now()
            )
            
            processing_result = self._execute_payment_processing(payment_transaction, payment_data)
            
            if processing_result['success']:
                payment_transaction.status = 'completed'
                payment_transaction.external_transaction_id = processing_result['transaction_id']
                payment_transaction.save()
                
                return {
                    'success': True,
                    'payment_id': payment_transaction.id,
                    'transaction_id': processing_result['transaction_id']
                }
            else:
                payment_transaction.status = 'failed'
                payment_transaction.failure_reason = processing_result.get('error', 'Unknown error')
                payment_transaction.save()
                return {'success': False, 'error': processing_result.get('error')}
    
    def _execute_payment_processing(self, payment_transaction: PaymentTransaction, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        if payment_data['method'] == 'credit_card':
            return self._process_credit_card_payment(payment_transaction, payment_data)
        elif payment_data['method'] == 'bank_transfer':
            return self._process_bank_transfer_payment(payment_transaction, payment_data)
        else:
            return {'success': False, 'error': 'Unsupported payment method'}
    
    def _process_credit_card_payment(self, payment_transaction: PaymentTransaction, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'transaction_id': f"cc_{payment_transaction.id}_{timezone.now().timestamp()}"
        }
    
    def _process_bank_transfer_payment(self, payment_transaction: PaymentTransaction, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'success': True,
            'transaction_id': f"bt_{payment_transaction.id}_{timezone.now().timestamp()}"
        }
    
    def _update_inventory_levels(self, order: Order) -> None:
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        
        for item in order_items:
            inventory = Inventory.objects.select_for_update().get(product=item.product)
            inventory.available_quantity -= item.quantity
            inventory.reserved_quantity += item.quantity
            inventory.save()
    
    def _finalize_order_status(self, order: Order) -> None:
        order.status = 'confirmed'
        order.confirmed_at = timezone.now()
        order.save()