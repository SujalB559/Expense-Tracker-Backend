from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from categories.models import Category


class CategoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jordan',
            email='jordan@example.com',
            password='password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_and_seed_categories(self):
        url = reverse('category_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should auto-seed defaults (8 expense + 5 income = 13 total)
        self.assertGreaterEqual(len(response.data), 13)

    def test_create_custom_category(self):
        url = reverse('category_list_create')
        data = {
            'name': 'Pet care',
            'type': 'expense',
            'icon': '🐾',
            'limit': 150.00,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Pet care')
        self.assertEqual(response.data['is_default'], False)

    def test_cannot_delete_default_category(self):
        cat = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense',
            is_default=True,
        )
        url = reverse('category_detail', kwargs={'pk': cat.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
