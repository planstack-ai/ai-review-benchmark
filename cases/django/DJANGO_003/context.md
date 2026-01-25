# Existing Codebase

## Schema

```python
# migrations/0001_initial.py
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock_count', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_stock_check', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=models.CASCADE, to='inventory.product')),
                ('alert_type', models.CharField(max_length=20, choices=[('LOW_STOCK', 'Low Stock'), ('OUT_OF_STOCK', 'Out of Stock')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(null=True, blank=True)),
            ],
        ),
    ]
```

## Models

```python
from decimal import Decimal
from typing import Any
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


class ProductQuerySet(models.QuerySet):
    def active(self) -> 'ProductQuerySet':
        return self.filter(is_active=True)
    
    def low_stock(self, threshold: int = 10) -> 'ProductQuerySet':
        return self.filter(stock_count__lte=threshold)
    
    def out_of_stock(self) -> 'ProductQuerySet':
        return self.filter(stock_count=0)


class ProductManager(models.Manager):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)
    
    def active(self) -> ProductQuerySet:
        return self.get_queryset().active()
    
    def bulk_update_stock(self, updates: dict[int, int]) -> int:
        """Bulk update stock counts for multiple products."""
        products = []
        for product_id, new_stock in updates.items():
            try:
                product = self.get(id=product_id)
                product.stock_count = new_stock
                products.append(product)
            except self.model.DoesNotExist:
                continue
        
        if products:
            return self.bulk_update(products, ['stock_count'], batch_size=100)
        return 0


class Product(models.Model):
    LOW_STOCK_THRESHOLD = 10
    
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_stock_check = models.DateTimeField(null=True, blank=True)
    
    objects = ProductManager()
    
    def save(self, *args, **kwargs) -> None:
        is_new = self.pk is None
        old_stock = None
        
        if not is_new:
            try:
                old_instance = Product.objects.get(pk=self.pk)
                old_stock = old_instance.stock_count
            except Product.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        if old_stock is not None and old_stock != self.stock_count:
            self._handle_stock_change(old_stock)
        elif is_new and self.stock_count <= self.LOW_STOCK_THRESHOLD:
            self._create_stock_alert()
    
    def _handle_stock_change(self, old_stock: int) -> None:
        """Handle stock level changes and create alerts if needed."""
        self.last_stock_check = timezone.now()
        self.save(update_fields=['last_stock_check'])
        
        if self.stock_count <= self.LOW_STOCK_THRESHOLD and old_stock > self.LOW_STOCK_THRESHOLD:
            self._create_stock_alert()
        elif self.stock_count == 0 and old_stock > 0:
            self._create_stock_alert(alert_type='OUT_OF_STOCK')
    
    def _create_stock_alert(self, alert_type: str = 'LOW_STOCK') -> None:
        """Create a stock alert for this product."""
        StockAlert.objects.create(product=self, alert_type=alert_type)
        self._send_stock_notification(alert_type)
    
    def _send_stock_notification(self, alert_type: str) -> None:
        """Send email notification for stock alerts."""
        subject = f"Stock Alert: {self.name}"
        message = f"Product {self.name} is {'out of stock' if alert_type == 'OUT_OF_STOCK' else 'low on stock'}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.INVENTORY_EMAIL])


class StockAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'Low Stock'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
```