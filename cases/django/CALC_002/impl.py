from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class OrderItem:
    product_id: int
    quantity: int
    unit_price: Decimal
    name: str


@dataclass
class DiscountRule:
    code: str
    percentage: Decimal
    minimum_amount: Decimal


class TaxCalculationService:
    TAX_RATE = Decimal('0.10')
    
    def __init__(self):
        self.applied_discounts = []
    
    def calculate_order_total(self, items: List[OrderItem], discount_code: Optional[str] = None) -> Dict[str, Decimal]:
        if not items:
            raise ValidationError("Order must contain at least one item")
        
        subtotal = self._calculate_subtotal(items)
        discount_amount = self._calculate_discount(subtotal, discount_code)
        tax_amount = self._calculate_tax(subtotal, discount_amount)
        total = self._calculate_final_total(subtotal, discount_amount, tax_amount)
        
        return {
            'subtotal': subtotal,
            'discount': discount_amount,
            'tax': tax_amount,
            'total': total
        }
    
    def _calculate_subtotal(self, items: List[OrderItem]) -> Decimal:
        subtotal = Decimal('0.00')
        for item in items:
            if item.quantity <= 0 or item.unit_price < 0:
                raise ValidationError(f"Invalid item data for product {item.product_id}")
            subtotal += item.unit_price * item.quantity
        return subtotal.quantize(Decimal('0.01'))
    
    def _calculate_discount(self, subtotal: Decimal, discount_code: Optional[str]) -> Decimal:
        if not discount_code:
            return Decimal('0.00')
        
        discount_rule = self._get_discount_rule(discount_code)
        if not discount_rule:
            return Decimal('0.00')
        
        if subtotal < discount_rule.minimum_amount:
            return Decimal('0.00')
        
        discount_amount = subtotal * (discount_rule.percentage / Decimal('100'))
        self.applied_discounts.append(discount_rule.code)
        
        return discount_amount.quantize(Decimal('0.01'))
    
    def _calculate_tax(self, subtotal: Decimal, discount_amount: Decimal) -> Decimal:
        taxable_amount = (subtotal * (Decimal('1') + self.TAX_RATE)) - discount_amount
        tax_amount = taxable_amount - subtotal + discount_amount
        return tax_amount.quantize(Decimal('0.01'))
    
    def _calculate_final_total(self, subtotal: Decimal, discount_amount: Decimal, tax_amount: Decimal) -> Decimal:
        total = subtotal + tax_amount - discount_amount
        return total.quantize(Decimal('0.01'))
    
    def _get_discount_rule(self, code: str) -> Optional[DiscountRule]:
        discount_rules = {
            'SAVE10': DiscountRule('SAVE10', Decimal('10'), Decimal('50.00')),
            'SAVE20': DiscountRule('SAVE20', Decimal('20'), Decimal('100.00')),
            'WELCOME5': DiscountRule('WELCOME5', Decimal('5'), Decimal('25.00'))
        }
        return discount_rules.get(code.upper())
    
    @transaction.atomic
    def process_order_calculation(self, order_data: Dict) -> Dict[str, Decimal]:
        items = []
        for item_data in order_data.get('items', []):
            items.append(OrderItem(
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=Decimal(str(item_data['unit_price'])),
                name=item_data.get('name', f"Product {item_data['product_id']}")
            ))
        
        discount_code = order_data.get('discount_code')
        return self.calculate_order_total(items, discount_code)
    
    def get_applied_discounts(self) -> List[str]:
        return self.applied_discounts.copy()
    
    def reset_applied_discounts(self) -> None:
        self.applied_discounts.clear()