from django.contrib import admin
from .models import MonthlyBudget, SavingsGoal


@admin.register(MonthlyBudget)
class MonthlyBudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'updated_at')


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target', 'saved', 'progress', 'created_at')
