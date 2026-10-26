from django.urls import path
from .views import MonthlyBudgetView, SavingsGoalDetailView, SavingsGoalListCreateView

urlpatterns = [
    path('', MonthlyBudgetView.as_view(), name='monthly_budget'),
    path('goals/', SavingsGoalListCreateView.as_view(), name='savings_goal_list_create'),
    path('goals/<int:pk>/', SavingsGoalDetailView.as_view(), name='savings_goal_detail'),
]
