from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'type', 'category', 'date', 'user', 'recurring', 'created_at')
    list_filter = ('type', 'category', 'recurring', 'date')
    search_fields = ('name', 'category', 'description', 'user__username')
    date_hierarchy = 'date'
