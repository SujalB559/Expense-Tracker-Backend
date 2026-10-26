from django.conf import settings
from django.db import models


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('savings', 'Savings'),
    )

    REPEAT_CHOICES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='expense')
    category = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    recurring = models.BooleanField(default=False)
    repeat = models.CharField(
        max_length=20,
        blank=True,
        default='monthly',
        choices=REPEAT_CHOICES,
    )
    icon = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.type})"
