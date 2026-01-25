from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db import transaction
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone
from myapp.models import Product, Category, Inventory


class ProductBulkUpdateService:
    
    def __init__(self):
        self.batch_size = 1000
        self.updated_count = 0
    
    def bulk_update_prices(self, price_updates: Dict[int, Decimal]) -> int:
        if not price_updates:
            return 0
        
        product_ids = list(price_updates.keys())
        products = self._get_products_for_update(product_ids)
        
        if len(products) != len(product_ids):
            missing_ids = set(product_ids) - {p.id for p in products}
            raise ValidationError(f"Products not found: {missing_ids}")
        
        updated_products = self._prepare_price_updates(products, price_updates)
        return self._execute_bulk_update(updated_products, ['price', 'updated_at'])
    
    def bulk_update_inventory(self, inventory_data: List[Dict[str, Any]]) -> int:
        if not inventory_data:
            return 0
        
        product_ids = [item['product_id'] for item in inventory_data]
        products = self._get_products_for_update(product_ids)
        product_map = {p.id: p for p in products}
        
        updated_products = []
        for item in inventory_data:
            product_id = item['product_id']
            if product_id not in product_map:
                continue
            
            product = product_map[product_id]
            product.stock_quantity = item.get('quantity', product.stock_quantity)
            product.low_stock_threshold = item.get('threshold', product.low_stock_threshold)
            product.updated_at = timezone.now()
            updated_products.append(product)
        
        return self._execute_bulk_update(updated_products, 
                                       ['stock_quantity', 'low_stock_threshold', 'updated_at'])
    
    def bulk_update_categories(self, category_assignments: Dict[int, int]) -> int:
        product_ids = list(category_assignments.keys())
        category_ids = list(category_assignments.values())
        
        products = self._get_products_for_update(product_ids)
        valid_categories = set(Category.objects.filter(id__in=category_ids).values_list('id', flat=True))
        
        updated_products = []
        for product in products:
            new_category_id = category_assignments.get(product.id)
            if new_category_id and new_category_id in valid_categories:
                product.category_id = new_category_id
                product.updated_at = timezone.now()
                updated_products.append(product)
        
        return self._execute_bulk_update(updated_products, ['category_id', 'updated_at'])
    
    def _get_products_for_update(self, product_ids: List[int]) -> List[Product]:
        return list(Product.objects.filter(id__in=product_ids).select_for_update())
    
    def _prepare_price_updates(self, products: List[Product], 
                             price_updates: Dict[int, Decimal]) -> List[Product]:
        updated_products = []
        for product in products:
            new_price = price_updates.get(product.id)
            if new_price and new_price != product.price:
                product.price = new_price
                product.updated_at = timezone.now()
                updated_products.append(product)
        return updated_products
    
    @transaction.atomic
    def _execute_bulk_update(self, products: List[Product], fields: List[str]) -> int:
        if not products:
            return 0
        
        Product.objects.bulk_update(products, fields, batch_size=self.batch_size)
        self.updated_count += len(products)
        return len(products)