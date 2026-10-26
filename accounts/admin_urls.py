from django.urls import path
from .admin_views import (
    AdminStatsView,
    AdminUsersListView,
    AdminUserDeleteView,
    AdminTransactionsListView,
)

urlpatterns = [
    path('stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('users/', AdminUsersListView.as_view(), name='admin_users_list'),
    path('users/<int:pk>/', AdminUserDeleteView.as_view(), name='admin_user_delete'),
    path('transactions/', AdminTransactionsListView.as_view(), name='admin_transactions_list'),
]
