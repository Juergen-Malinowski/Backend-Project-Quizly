"""Reusable test helpers for authentication API tests."""

from django.contrib.auth import get_user_model
from django.urls import reverse


class AuthTestMixin:
    """Provides shared helpers for authentication endpoint tests."""

    def get_register_url(self):
        """Returns the registration endpoint URL."""

        return reverse('register')


    def get_login_url(self):
        """Returns the login endpoint URL."""

        return reverse('login')


    def get_user_count(self):
        """Returns the current number of stored users."""

        return get_user_model().objects.count()


    def create_test_user(self):
        """Creates a reusable existing user for validation tests."""

        return get_user_model().objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password='SecurePass123!',
        )


    def get_valid_registration_data(self):
        """Returns valid registration payload data."""

        return {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!',
        }


    def get_valid_login_data(self):
        """Returns valid login payload data."""

        return {
            'username': 'test_user',
            'password': 'SecurePass123!',
        }
