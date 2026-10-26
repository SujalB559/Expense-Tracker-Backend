from django.conf import settings
from django.db import models


class MonthlyBudget(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budget',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=2000.00,
        help_text="Overall monthly spending limit",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Budget: {self.amount}"


class SavingsGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_goals',
    )
    name = models.CharField(max_length=150)
    target = models.DecimalField(max_digits=12, decimal_places=2)
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.saved}/{self.target})"

    @property
    def progress(self):
        if self.target and self.target > 0:
            return min(round(float(self.saved / self.target) * 100), 100)
        return 0
