# Existing Codebase

## Schema

```python
# migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(primary_key=True)),
                ('email', models.EmailField(unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('department_code', models.CharField(max_length=10)),
                ('hire_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
```

## Models

```python
from django.db import models
from django.core.exceptions import ValidationError
from typing import Optional

class DepartmentManager(models.Manager):
    def active_departments(self):
        return self.filter(employee__is_active=True).distinct()
    
    def get_by_code(self, code: str) -> Optional['Department']:
        try:
            return self.get(code=code)
        except Department.DoesNotExist:
            return None

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = DepartmentManager()
    
    class Meta:
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
    @property
    def employee_count(self) -> int:
        return Employee.objects.filter(department_code=self.code, is_active=True).count()

class EmployeeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def by_department(self, department_code: str):
        return self.filter(department_code=department_code)
    
    def with_valid_departments(self):
        valid_codes = Department.objects.values_list('code', flat=True)
        return self.filter(department_code__in=valid_codes)

class EmployeeManager(models.Manager):
    def get_queryset(self):
        return EmployeeQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def by_department(self, department_code: str):
        return self.get_queryset().by_department(department_code)

class Employee(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department_code = models.CharField(max_length=10)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    objects = EmployeeManager()
    
    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['department_code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def get_department(self) -> Optional[Department]:
        return Department.objects.get_by_code(self.department_code)
```