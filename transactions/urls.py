from django.urls import path
from .views import (
    ClearTransactionsView,
    TransactionDetailView,
    TransactionListCreateView,
    TransactionSummaryView,
)

urlpatterns = [
    path('', TransactionListCreateView.as_view(), name='transaction_list_create'),
    path('summary/', TransactionSummaryView.as_view(), name='transaction_summary'),
    path('clear/', ClearTransactionsView.as_view(), name='transaction_clear'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
]
