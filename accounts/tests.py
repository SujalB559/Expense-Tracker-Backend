from datetime import timedelta
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import EmailVerificationToken, User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        url = reverse('auth_register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'currency': '$',
            'theme': 'light',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['initials'], 'TU')
        self.assertFalse(response.data['is_email_verified'])
        self.assertNotIn('tokens', response.data)
        self.assertNotIn('verification_link', response.data)

        # Check DB state
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_email_verified)
        self.assertTrue(EmailVerificationToken.objects.filter(user=user, is_used=False).exists())

    def test_login_unverified_user_blocked(self):
        User.objects.create_user(
            username='jordan',
            email='jordan@example.com',
            password='password123',
            is_email_verified=False,
        )
        url = reverse('auth_login')
        data = {
            'username': 'jordan',
            'password': 'password123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'email_not_verified')

    def test_login_verified_user_success(self):
        User.objects.create_user(
            username='jordan',
            email='jordan@example.com',
            password='password123',
            is_email_verified=True,
        )
        url = reverse('auth_login')
        data = {
            'username': 'jordan',
            'password': 'password123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_verify_email_flow(self):
        user = User.objects.create_user(
            username='pendinguser',
            email='pending@example.com',
            password='password123',
            is_email_verified=False,
        )
        token_obj = EmailVerificationToken.create_token(user)

        url = reverse('auth_verify_email')
        response = self.client.post(url, {'token': token_obj.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.is_used)

    def test_verify_email_already_verified(self):
        user = User.objects.create_user(
            username='activeuser',
            email='active@example.com',
            password='password123',
            is_email_verified=True,
        )
        token_obj = EmailVerificationToken.create_token(user)
        url = reverse('auth_verify_email')
        response = self.client.post(url, {'token': token_obj.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('already_verified'))

    def test_verify_email_invalid_token(self):
        url = reverse('auth_verify_email')
        response = self.client.post(url, {'token': 'invalid-token-12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'invalid_token')

    def test_verify_email_expired_token(self):
        user = User.objects.create_user(
            username='expireduser',
            email='expired@example.com',
            password='password123',
            is_email_verified=False,
        )
        token_obj = EmailVerificationToken.objects.create(
            user=user,
            token='expired-token-xyz',
            expires_at=timezone.now() - timedelta(hours=1),
            is_used=False,
        )
        url = reverse('auth_verify_email')
        response = self.client.post(url, {'token': token_obj.token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'token_expired')

    def test_resend_verification_email(self):
        user = User.objects.create_user(
            username='resenduser',
            email='resend@example.com',
            password='password123',
            is_email_verified=False,
        )
        old_token = EmailVerificationToken.create_token(user)

        url = reverse('auth_resend_verification')
        response = self.client.post(url, {'email': user.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['email_sent'])
        self.assertNotIn('verification_link', response.data)

        # Check old token was replaced by fresh token
        self.assertFalse(EmailVerificationToken.objects.filter(id=old_token.id).exists())
        self.assertTrue(EmailVerificationToken.objects.filter(user=user, is_used=False).exists())

    def test_current_user_me(self):
        user = User.objects.create_user(
            username='jordan',
            email='jordan@example.com',
            password='password123',
            first_name='Jordan',
            last_name='Davis',
            is_email_verified=True,
        )
        self.client.force_authenticate(user=user)
        url = reverse('auth_me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'jordan')
        self.assertEqual(response.data['full_name'], 'Jordan Davis')

        # Test updating preferences
        patch_response = self.client.patch(url, {'currency': '€', 'theme': 'dark'}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['currency'], '€')
        self.assertEqual(patch_response.data['theme'], 'dark')
