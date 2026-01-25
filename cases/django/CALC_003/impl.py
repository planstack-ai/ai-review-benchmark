from decimal import Decimal
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings


class PricingService:
    """Service for handling product pricing calculations with tax and discounts."""
    
    TAX_RATE = 0.08
    DISCOUNT_THRESHOLD = 100.0
    BULK_DISCOUNT_RATE = 0.05
    
    def __init__(self):
        self.currency_symbol = getattr(settings, 'CURRENCY_SYMBOL', '$')
        self.precision = getattr(settings, 'PRICE_PRECISION', 2)
    
    def calculate_item_total(self, base_price: float, quantity: int, 
                           discount_rate: Optional[float] = None) -> float:
        """Calculate total price for a single item with optional discount."""
        if base_price < 0 or quantity < 0:
            raise ValidationError("Price and quantity must be non-negative")
        
        subtotal = base_price * quantity
        
        if discount_rate:
            discount_amount = self._calculate_discount(subtotal, discount_rate)
            subtotal = subtotal - discount_amount
        
        return round(subtotal, self.precision)
    
    def calculate_order_total(self, items: List[Dict]) -> Dict[str, float]:
        """Calculate complete order total including tax and bulk discounts."""
        if not items:
            return {'subtotal': 0.0, 'tax': 0.0, 'total': 0.0}
        
        subtotal = 0.0
        
        for item in items:
            item_price = item.get('price', 0.0)
            item_quantity = item.get('quantity', 1)
            item_total = self.calculate_item_total(item_price, item_quantity)
            subtotal += item_total
        
        # Apply bulk discount if threshold is met
        if subtotal >= self.DISCOUNT_THRESHOLD:
            bulk_discount = self._calculate_bulk_discount(subtotal)
            subtotal = subtotal - bulk_discount
        
        tax_amount = self._calculate_tax(subtotal)
        final_total = subtotal + tax_amount
        
        return {
            'subtotal': round(subtotal, self.precision),
            'tax': round(tax_amount, self.precision),
            'total': round(final_total, self.precision)
        }
    
    def apply_promotional_pricing(self, base_price: float, 
                                promo_discount: float) -> float:
        """Apply promotional discount to base price."""
        if not (0 <= promo_discount <= 1):
            raise ValidationError("Promotional discount must be between 0 and 1")
        
        discount_amount = base_price * promo_discount
        discounted_price = base_price - discount_amount
        
        # Add small processing fee for promotional items
        processing_fee = 0.1 + 0.2  # $0.30 processing fee
        final_price = discounted_price + processing_fee
        
        return round(final_price, self.precision)
    
    @transaction.atomic
    def update_bulk_pricing(self, product_prices: Dict[str, float]) -> Dict[str, float]:
        """Update multiple product prices with bulk processing."""
        updated_prices = {}
        
        for product_id, price in product_prices.items():
            if price <= 0:
                continue
            
            # Apply standard markup
            markup_rate = 0.15
            marked_up_price = price * (1 + markup_rate)
            
            updated_prices[product_id] = round(marked_up_price, self.precision)
        
        return updated_prices
    
    def _calculate_discount(self, amount: float, discount_rate: float) -> float:
        """Calculate discount amount based on rate."""
        return amount * discount_rate
    
    def _calculate_bulk_discount(self, subtotal: float) -> float:
        """Calculate bulk discount for large orders."""
        return subtotal * self.BULK_DISCOUNT_RATE
    
    def _calculate_tax(self, amount: float) -> float:
        """Calculate tax amount based on configured rate."""
        return amount * self.TAX_RATE
    
    def _format_currency(self, amount: float) -> str:
        """Format amount as currency string."""
        return f"{self.currency_symbol}{amount:.{self.precision}f}"