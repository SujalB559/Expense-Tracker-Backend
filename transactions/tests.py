from datetime import date
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from transactions.models import Transaction


class TransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jordan',
            email='jordan@example.com',
            password='password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_and_list_transactions(self):
        url = reverse('transaction_list_create')
        data = {
            'name': 'Whole Foods Market',
            'amount': 86.40,
            'type': 'expense',
            'category': 'Food',
            'date': '2024-06-08',
            'description': 'Weekly groceries',
            'recurring': False,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Whole Foods Market')
        self.assertEqual(response.data['amount'], 86.40)
        self.assertEqual(response.data['icon'], '🍔')  # Resolved automatically

        list_resp = self.client.get(url)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_resp.data), 1)

    def test_summary_calculation(self):
        Transaction.objects.create(
            user=self.user,
            name='Salary',
            amount=5000.00,
            type='income',
            category='Salary',
            date=date.today(),
        )
        Transaction.objects.create(
            user=self.user,
            name='Groceries',
            amount=1000.00,
            type='expense',
            category='Food',
            date=date.today(),
        )
        url = reverse('transaction_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['income'], 5000.00)
        self.assertEqual(response.data['expenses'], 1000.00)
        self.assertEqual(response.data['balance'], 4000.00)
        self.assertEqual(response.data['savingsRate'], 80)

    def test_summary_calculation_with_savings(self):
        Transaction.objects.create(
            user=self.user,
            name='Salary',
            amount=5000.00,
            type='income',
            category='Salary',
            date=date.today(),
        )
        Transaction.objects.create(
            user=self.user,
            name='Groceries',
            amount=1000.00,
            type='expense',
            category='Food',
            date=date.today(),
        )
        Transaction.objects.create(
            user=self.user,
            name='Emergency Fund',
            amount=500.00,
            type='savings',
            category='Savings',
            date=date.today(),
        )
        url = reverse('transaction_summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['income'], 5000.00)
        self.assertEqual(response.data['expenses'], 1000.00)
        self.assertEqual(response.data['savings'], 500.00)
        # Total balance should deduct both expenses and savings: 5000 - 1000 - 500 = 3500
        self.assertEqual(response.data['balance'], 3500.00)
