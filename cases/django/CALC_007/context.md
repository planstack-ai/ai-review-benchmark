# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_points (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    total_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE point_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    order_id INTEGER,
    points INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Models

```python
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def final_amount(self) -> Decimal:
        """Amount after applying discount"""
        return max(self.total_amount - self.discount_amount, Decimal('0.00'))
    
    def mark_as_paid(self) -> None:
        """Mark order as paid and trigger point calculation"""
        self.status = 'paid'
        self.save(update_fields=['status', 'updated_at'])


class UserPointsManager(models.Manager):
    def get_or_create_for_user(self, user: User) -> tuple['UserPoints', bool]:
        return self.get_or_create(user=user, defaults={'total_points': 0})


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserPointsManager()
    
    class Meta:
        verbose_name_plural = "User points"
    
    def add_points(self, points: int, order: Order = None) -> 'PointTransaction':
        """Add points and create transaction record"""
        self.total_points += points
        self.save(update_fields=['total_points', 'updated_at'])
        
        return PointTransaction.objects.create(
            user=self.user,
            order=order,
            points=points,
            transaction_type='earned'
        )


class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


# Constants
POINTS_PER_DOLLAR = 10
MIN_ORDER_AMOUNT_FOR_POINTS = Decimal('5.00')
```