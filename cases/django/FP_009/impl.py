from decimal import Decimal
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError


class PricingService:
    
    BASE_DISCOUNT_THRESHOLD = Decimal('1000.00')
    VOLUME_DISCOUNT_RATES = {
        Decimal('5000.00'): Decimal('0.15'),
        Decimal('2500.00'): Decimal('0.10'),
        Decimal('1000.00'): Decimal('0.05'),
    }
    TAX_RATE = Decimal('0.08')
    SHIPPING_RATES = {
        'standard': Decimal('9.99'),
        'express': Decimal('19.99'),
        'overnight': Decimal('39.99'),
    }
    
    def __init__(self, customer_tier: str = 'regular'):
        self.customer_tier = customer_tier
        self.tier_multipliers = {
            'premium': Decimal('0.95'),
            'gold': Decimal('0.90'),
            'regular': Decimal('1.00'),
        }
    
    def calculate_total_price(self, items: List[Dict], shipping_method: str = 'standard', 
                            apply_tax: bool = True, coupon_code: Optional[str] = None) -> Dict:
        if not items:
            raise ValidationError("Items list cannot be empty")
        
        subtotal = self._calculate_subtotal(items)
        volume_discount = self._calculate_volume_discount(subtotal)
        tier_discount = self._apply_tier_discount(subtotal - volume_discount)
        coupon_discount = self._apply_coupon_discount(coupon_code, subtotal)
        
        discounted_total = subtotal - volume_discount - tier_discount - coupon_discount
        shipping_cost = self._calculate_shipping(discounted_total, shipping_method)
        
        pre_tax_total = discounted_total + shipping_cost
        tax_amount = self._calculate_tax(pre_tax_total) if apply_tax else Decimal('0.00')
        final_total = pre_tax_total + tax_amount
        
        return {
            'subtotal': subtotal,
            'volume_discount': volume_discount,
            'tier_discount': tier_discount,
            'coupon_discount': coupon_discount,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'final_total': final_total,
        }
    
    def _calculate_subtotal(self, items: List[Dict]) -> Decimal:
        subtotal = Decimal('0.00')
        for item in items:
            price = Decimal(str(item.get('price', 0)))
            quantity = int(item.get('quantity', 1))
            subtotal += price * quantity
        return subtotal
    
    def _calculate_volume_discount(self, subtotal: Decimal) -> Decimal:
        for threshold, rate in sorted(self.VOLUME_DISCOUNT_RATES.items(), reverse=True):
            if subtotal >= threshold:
                return subtotal * rate
        return Decimal('0.00')
    
    def _apply_tier_discount(self, amount: Decimal) -> Decimal:
        multiplier = self.tier_multipliers.get(self.customer_tier, Decimal('1.00'))
        if multiplier < Decimal('1.00'):
            return amount * (Decimal('1.00') - multiplier)
        return Decimal('0.00')
    
    def _apply_coupon_discount(self, coupon_code: Optional[str], subtotal: Decimal) -> Decimal:
        if not coupon_code:
            return Decimal('0.00')
        
        coupon_rates = {
            'SAVE10': Decimal('0.10'),
            'WELCOME5': Decimal('0.05'),
            'BULK20': Decimal('0.20') if subtotal >= Decimal('500.00') else Decimal('0.00'),
        }
        
        return subtotal * coupon_rates.get(coupon_code.upper(), Decimal('0.00'))
    
    def _calculate_shipping(self, total: Decimal, method: str) -> Decimal:
        if total >= Decimal('100.00') and method == 'standard':
            return Decimal('0.00')
        return self.SHIPPING_RATES.get(method, self.SHIPPING_RATES['standard'])
    
    def _calculate_tax(self, amount: Decimal) -> Decimal:
        return amount * self.TAX_RATE
    
    @transaction.atomic
    def process_bulk_pricing(self, order_data: List[Dict]) -> List[Dict]:
        results = []
        for order in order_data:
            pricing_result = self.calculate_total_price(
                items=order.get('items', []),
                shipping_method=order.get('shipping_method', 'standard'),
                apply_tax=order.get('apply_tax', True),
                coupon_code=order.get('coupon_code')
            )
            results.append({
                'order_id': order.get('order_id'),
                'pricing': pricing_result
            })
        return results