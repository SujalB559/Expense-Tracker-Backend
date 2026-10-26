from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'user', 'is_default', 'limit', 'icon', 'created_at')
    list_filter = ('type', 'is_default')
    search_fields = ('name', 'user__username')
