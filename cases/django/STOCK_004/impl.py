from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional
from .models import Product, StockReservation, StockMovement


class StockManagementService:
    """Service for managing product stock levels and reservations."""
    
    def __init__(self):
        self.minimum_stock_threshold = Decimal('5.00')
    
    def get_stock_summary(self, product_id: int) -> Dict[str, Decimal]:
        """Get comprehensive stock information for a product."""
        product = Product.objects.get(id=product_id)
        reserved_stock = self._calculate_reserved_stock(product_id)
        
        return {
            'total_stock': product.stock_quantity,
            'reserved_stock': reserved_stock,
            'available_stock': product.stock_quantity,
            'low_stock_alert': product.stock_quantity < self.minimum_stock_threshold
        }
    
    def reserve_stock(self, product_id: int, quantity: Decimal, 
                     reservation_reference: str) -> bool:
        """Reserve stock for a specific order or customer."""
        with transaction.atomic():
            stock_info = self.get_stock_summary(product_id)
            
            if stock_info['available_stock'] < quantity:
                raise ValidationError(
                    f"Insufficient stock. Available: {stock_info['available_stock']}, "
                    f"Requested: {quantity}"
                )
            
            StockReservation.objects.create(
                product_id=product_id,
                quantity=quantity,
                reference=reservation_reference,
                status='active'
            )
            
            self._log_stock_movement(
                product_id, -quantity, 'reservation', reservation_reference
            )
            
            return True
    
    def release_reservation(self, reservation_reference: str) -> bool:
        """Release a stock reservation back to available inventory."""
        with transaction.atomic():
            reservation = StockReservation.objects.get(
                reference=reservation_reference,
                status='active'
            )
            
            reservation.status = 'released'
            reservation.save()
            
            self._log_stock_movement(
                reservation.product_id, 
                reservation.quantity, 
                'release', 
                reservation_reference
            )
            
            return True
    
    def fulfill_reservation(self, reservation_reference: str) -> bool:
        """Convert a reservation to actual stock consumption."""
        with transaction.atomic():
            reservation = StockReservation.objects.get(
                reference=reservation_reference,
                status='active'
            )
            
            product = Product.objects.select_for_update().get(
                id=reservation.product_id
            )
            
            if product.stock_quantity < reservation.quantity:
                raise ValidationError("Insufficient physical stock for fulfillment")
            
            product.stock_quantity -= reservation.quantity
            product.save()
            
            reservation.status = 'fulfilled'
            reservation.save()
            
            self._log_stock_movement(
                reservation.product_id,
                -reservation.quantity,
                'fulfillment',
                reservation_reference
            )
            
            return True
    
    def _calculate_reserved_stock(self, product_id: int) -> Decimal:
        """Calculate total reserved stock for a product."""
        reservations = StockReservation.objects.filter(
            product_id=product_id,
            status='active'
        )
        
        return sum(reservation.quantity for reservation in reservations)
    
    def _log_stock_movement(self, product_id: int, quantity_change: Decimal,
                           movement_type: str, reference: str) -> None:
        """Log stock movement for audit trail."""
        StockMovement.objects.create(
            product_id=product_id,
            quantity_change=quantity_change,
            movement_type=movement_type,
            reference=reference
        )