# Existing Codebase

## Schema

```sql
CREATE TABLE coupons_coupon (
    id BIGINT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    owner_id BIGINT NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES auth_user(id)
);

CREATE TABLE orders_order (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    coupon_id BIGINT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (coupon_id) REFERENCES coupons_coupon(id)
);
```

## Models

```python
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CouponQuerySet(models.QuerySet):
    def active(self):
        return self.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        )
    
    def for_user(self, user: User):
        return self.filter(owner=user)


class CouponManager(models.Manager):
    def get_queryset(self):
        return CouponQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def for_user(self, user: User):
        return self.get_queryset().for_user(user)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupons')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CouponManager()
    
    class Meta:
        db_table = 'coupons_coupon'
    
    def __str__(self) -> str:
        return f"{self.code} - {self.owner.username}"
    
    def is_valid(self) -> bool:
        return self.is_active and self.expires_at > timezone.now()
    
    def can_be_used_by(self, user: User) -> bool:
        return self.owner == user and self.is_valid()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders_order'
    
    def apply_coupon(self, coupon: Coupon) -> None:
        if not coupon.can_be_used_by(self.user):
            raise ValidationError("Invalid coupon for this user")
        
        self.coupon = coupon
        self.discount_applied = min(coupon.discount_amount, self.total_amount)
        self.save()
    
    @property
    def final_amount(self) -> Decimal:
        return self.total_amount - self.discount_applied
```