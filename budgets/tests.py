from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from budgets.models import MonthlyBudget


class BudgetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jordan',
            email='jordan@example.com',
            password='password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_and_update_budget(self):
        url = reverse('monthly_budget')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 2000.00)

        # Update budget
        put_response = self.client.put(url, {'amount': 3500.00}, format='json')
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.data['amount'], 3500.00)

    def test_savings_goals(self):
        url = reverse('savings_goal_list_create')
        data = {
            'name': 'Emergency Fund',
            'target': 5000.00,
            'saved': 2500.00,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['progress'], 50)
