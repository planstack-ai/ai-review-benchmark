from decimal import Decimal
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from myapp.models import Product, WarehouseStock, SyncLog


class InventorySyncService:
    """Service for managing inventory synchronization with external warehouses."""
    
    def __init__(self):
        self.sync_delay_threshold = 300  # 5 minutes in seconds
        
    def get_available_stock(self, product_id: int, warehouse_id: int) -> Decimal:
        """Calculate available stock for a product in a specific warehouse."""
        try:
            warehouse_stock = WarehouseStock.objects.get(
                product_id=product_id,
                warehouse_id=warehouse_id
            )
            
            local_stock = warehouse_stock.quantity
            reserved_stock = self._get_reserved_quantity(product_id, warehouse_id)
            
            available = local_stock - reserved_stock
            
            return max(Decimal('0'), available)
            
        except WarehouseStock.DoesNotExist:
            return Decimal('0')
    
    def sync_warehouse_inventory(self, warehouse_id: int) -> Dict[str, int]:
        """Synchronize inventory data with external warehouse system."""
        sync_results = {'updated': 0, 'errors': 0}
        
        try:
            external_data = self._fetch_external_inventory(warehouse_id)
            
            with transaction.atomic():
                for item in external_data:
                    try:
                        self._update_warehouse_stock(
                            warehouse_id,
                            item['product_id'],
                            item['quantity']
                        )
                        sync_results['updated'] += 1
                    except Exception as e:
                        sync_results['errors'] += 1
                        
                self._log_sync_operation(warehouse_id, sync_results)
                
        except Exception as e:
            sync_results['errors'] += 1
            
        return sync_results
    
    def check_sync_status(self, warehouse_id: int) -> bool:
        """Check if warehouse sync is up to date."""
        try:
            last_sync = SyncLog.objects.filter(
                warehouse_id=warehouse_id,
                status='completed'
            ).latest('created_at')
            
            time_diff = (timezone.now() - last_sync.created_at).total_seconds()
            return time_diff <= self.sync_delay_threshold
            
        except SyncLog.DoesNotExist:
            return False
    
    def _get_reserved_quantity(self, product_id: int, warehouse_id: int) -> Decimal:
        """Get quantity reserved for pending orders."""
        from myapp.models import OrderItem
        
        reserved = OrderItem.objects.filter(
            product_id=product_id,
            order__warehouse_id=warehouse_id,
            order__status__in=['pending', 'processing']
        ).aggregate(
            total=models.Sum('quantity')
        )['total'] or Decimal('0')
        
        return reserved
    
    def _fetch_external_inventory(self, warehouse_id: int) -> List[Dict]:
        """Fetch inventory data from external warehouse API."""
        # Simulate external API call
        return [
            {'product_id': 1, 'quantity': 100},
            {'product_id': 2, 'quantity': 50},
        ]
    
    def _update_warehouse_stock(self, warehouse_id: int, product_id: int, quantity: Decimal):
        """Update local warehouse stock record."""
        warehouse_stock, created = WarehouseStock.objects.get_or_create(
            warehouse_id=warehouse_id,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        
        if not created:
            warehouse_stock.quantity = quantity
            warehouse_stock.last_updated = timezone.now()
            warehouse_stock.save()
    
    def _log_sync_operation(self, warehouse_id: int, results: Dict[str, int]):
        """Log synchronization operation results."""
        SyncLog.objects.create(
            warehouse_id=warehouse_id,
            status='completed' if results['errors'] == 0 else 'partial',
            updated_count=results['updated'],
            error_count=results['errors'],
            created_at=timezone.now()
        )