import logging
from typing import List, Optional
from decimal import Decimal
from django.db import transaction, DatabaseError
from django.utils import timezone
from myapp.models import Product

logger = logging.getLogger(__name__)


class ProductBulkUpdateService:
    DEFAULT_BATCH_SIZE = 1000

    def __init__(self, batch_size: Optional[int] = None):
        self.batch_size = batch_size or self.DEFAULT_BATCH_SIZE

    def bulk_update_prices(self, product_ids: List[int], new_price: Decimal) -> int:
        if not product_ids:
            logger.info("bulk_update_prices called with empty product_ids list")
            return 0

        if not self._validate_price(new_price):
            raise ValueError("Price must be a positive number greater than zero")

        if not self._validate_product_ids(product_ids):
            raise ValueError("Product IDs must be valid positive integers")

        try:
            with transaction.atomic():
                products = list(
                    Product.objects.filter(id__in=product_ids).select_for_update()
                )

                existing_ids = {p.id for p in products}
                missing_ids = set(product_ids) - existing_ids

                if missing_ids:
                    logger.warning(
                        f"bulk_update_prices: {len(missing_ids)} product IDs not found: {missing_ids}"
                    )

                if not products:
                    logger.info("bulk_update_prices: No valid products found to update")
                    return 0

                now = timezone.now()
                for product in products:
                    product.price = new_price
                    product.updated_at = now

                updated_count = Product.objects.bulk_update(
                    products,
                    fields=['price', 'updated_at'],
                    batch_size=self.batch_size
                )

                logger.info(
                    f"bulk_update_prices: Successfully updated {updated_count} products "
                    f"to price {new_price}"
                )

                return updated_count

        except DatabaseError as e:
            logger.error(f"bulk_update_prices failed with database error: {e}")
            raise RuntimeError(f"Failed to update product prices: {e}")

    def bulk_update_stock(self, product_ids: List[int], quantity_delta: int) -> int:
        if not product_ids:
            return 0

        if not self._validate_product_ids(product_ids):
            raise ValueError("Product IDs must be valid positive integers")

        try:
            with transaction.atomic():
                products = list(
                    Product.objects.filter(id__in=product_ids).select_for_update()
                )

                if not products:
                    return 0

                now = timezone.now()
                for product in products:
                    new_quantity = product.stock_quantity + quantity_delta
                    if new_quantity < 0:
                        raise ValueError(
                            f"Cannot reduce stock below zero for product {product.id}"
                        )
                    product.stock_quantity = new_quantity
                    product.updated_at = now

                updated_count = Product.objects.bulk_update(
                    products,
                    fields=['stock_quantity', 'updated_at'],
                    batch_size=self.batch_size
                )

                logger.info(
                    f"bulk_update_stock: Updated {updated_count} products by {quantity_delta}"
                )

                return updated_count

        except DatabaseError as e:
            logger.error(f"bulk_update_stock failed with database error: {e}")
            raise RuntimeError(f"Failed to update product stock: {e}")

    def bulk_deactivate(self, product_ids: List[int]) -> int:
        if not product_ids:
            return 0

        if not self._validate_product_ids(product_ids):
            raise ValueError("Product IDs must be valid positive integers")

        try:
            with transaction.atomic():
                updated_count = Product.objects.filter(
                    id__in=product_ids,
                    is_active=True
                ).update(
                    is_active=False,
                    updated_at=timezone.now()
                )

                logger.info(f"bulk_deactivate: Deactivated {updated_count} products")

                return updated_count

        except DatabaseError as e:
            logger.error(f"bulk_deactivate failed with database error: {e}")
            raise RuntimeError(f"Failed to deactivate products: {e}")

    def _validate_price(self, price: Decimal) -> bool:
        if price is None:
            return False
        try:
            decimal_price = Decimal(str(price))
            return decimal_price > Decimal('0')
        except (ValueError, TypeError):
            return False

    def _validate_product_ids(self, product_ids: List[int]) -> bool:
        if not product_ids:
            return True
        return all(
            isinstance(pid, int) and pid > 0
            for pid in product_ids
        )
