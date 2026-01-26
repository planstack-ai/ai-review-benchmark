# Existing Codebase

## Schema

```sql
CREATE TABLE financial_periods (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(year, month)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(12, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    period_id INTEGER REFERENCES financial_periods(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Models

```python
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from django.db import models
from django.db.models import QuerySet, Sum
from django.utils import timezone


class FinancialPeriodQuerySet(models.QuerySet):
    def open_periods(self) -> QuerySet["FinancialPeriod"]:
        return self.filter(is_closed=False)
    
    def for_date(self, target_date: date) -> QuerySet["FinancialPeriod"]:
        return self.filter(
            start_date__lte=target_date,
            end_date__gte=target_date
        )
    
    def current_month(self) -> QuerySet["FinancialPeriod"]:
        today = timezone.now().date()
        return self.for_date(today)


class FinancialPeriodManager(models.Manager):
    def get_queryset(self) -> FinancialPeriodQuerySet:
        return FinancialPeriodQuerySet(self.model, using=self._db)
    
    def open_periods(self) -> QuerySet["FinancialPeriod"]:
        return self.get_queryset().open_periods()
    
    def for_date(self, target_date: date) -> QuerySet["FinancialPeriod"]:
        return self.get_queryset().for_date(target_date)


class FinancialPeriod(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = FinancialPeriodManager()
    
    class Meta:
        unique_together = [["year", "month"]]
        ordering = ["-year", "-month"]
    
    def __str__(self) -> str:
        return f"{self.year}-{self.month:02d}"
    
    @property
    def is_current_month(self) -> bool:
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    def get_total_transactions(self) -> Decimal:
        return self.transactions.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("failed", "Failed"),
    ]
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateField()
    period = models.ForeignKey(
        FinancialPeriod,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-transaction_date", "-created_at"]
    
    def assign_to_period(self) -> Optional["FinancialPeriod"]:
        period = FinancialPeriod.objects.for_date(self.transaction_date).first()
        if period:
            self.period = period
            self.save(update_fields=["period"])
        return period
```