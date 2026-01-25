from decimal import Decimal
from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from products.models import Product, PriceHistory
import logging

logger = logging.getLogger(__name__)


class ProductPriceService:
    """Service class for managing product price operations."""
    
    def __init__(self):
        self.max_price_change_percent = Decimal('50.0')
        self.min_price = Decimal('0.01')
    
    def update_product_price(self, product_id: int, new_price: Decimal, 
                           user: User, reason: str = '') -> Dict[str, Any]:
        """
        Updates the price of a product with validation and history tracking.
        
        Args:
            product_id: ID of the product to update
            new_price: New price to set
            user: User performing the update
            reason: Optional reason for price change
            
        Returns:
            Dictionary containing update status and details
        """
        try:
            product = Product.objects.select_for_update().get(id=product_id)
            
            if not self._validate_price_change(product, new_price):
                return {
                    'success': False,
                    'error': 'Price change validation failed',
                    'details': 'Price change exceeds maximum allowed percentage'
                }
            
            old_price = product.price
            
            with transaction.atomic():
                product.price = new_price
                product.last_modified = timezone.now()
                product.last_modified_by = user
                product.save()
                
                self._create_price_history_entry(
                    product=product,
                    old_price=old_price,
                    new_price=new_price,
                    user=user,
                    reason=reason
                )
            
            logger.info(f"Price updated for product {product_id} by user {user.username}")
            
            return {
                'success': True,
                'old_price': old_price,
                'new_price': new_price,
                'product_name': product.name
            }
            
        except Product.DoesNotExist:
            return {
                'success': False,
                'error': 'Product not found'
            }
        except Exception as e:
            logger.error(f"Error updating price for product {product_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Internal server error'
            }
    
    def bulk_update_prices(self, price_updates: Dict[int, Decimal], 
                          user: User, reason: str = '') -> Dict[str, Any]:
        """
        Updates multiple product prices in a single transaction.
        
        Args:
            price_updates: Dictionary mapping product IDs to new prices
            user: User performing the updates
            reason: Optional reason for price changes
            
        Returns:
            Dictionary containing bulk update results
        """
        results = {
            'successful_updates': [],
            'failed_updates': [],
            'total_processed': len(price_updates)
        }
        
        for product_id, new_price in price_updates.items():
            result = self.update_product_price(product_id, new_price, user, reason)
            
            if result['success']:
                results['successful_updates'].append({
                    'product_id': product_id,
                    'old_price': result['old_price'],
                    'new_price': result['new_price']
                })
            else:
                results['failed_updates'].append({
                    'product_id': product_id,
                    'error': result['error']
                })
        
        return results
    
    def _validate_price_change(self, product: Product, new_price: Decimal) -> bool:
        """Validates if the price change is within acceptable limits."""
        if new_price < self.min_price:
            return False
        
        if product.price == 0:
            return True
        
        price_change_percent = abs((new_price - product.price) / product.price * 100)
        return price_change_percent <= self.max_price_change_percent
    
    def _create_price_history_entry(self, product: Product, old_price: Decimal,
                                  new_price: Decimal, user: User, reason: str) -> None:
        """Creates a price history entry for audit purposes."""
        PriceHistory.objects.create(
            product=product,
            old_price=old_price,
            new_price=new_price,
            changed_by=user,
            change_reason=reason,
            change_date=timezone.now()
        )