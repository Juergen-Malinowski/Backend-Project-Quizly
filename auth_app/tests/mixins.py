"""Reusable test helpers for authentication API tests."""

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken


class AuthTestMixin:
    """Provides shared helpers for authentication endpoint tests."""

    def get_register_url(self):
        """Returns the registration endpoint URL."""

        return reverse('register')


    def get_login_url(self):
        """Returns the login endpoint URL."""

        return reverse('login')


    def get_logout_url(self):
        """Returns the logout endpoint URL."""

        return reverse('logout')


    def get_token_refresh_url(self):
        """Returns the token refresh endpoint URL."""

        return reverse('token-refresh')


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


    def authenticate_with_cookie_tokens(self):
        """Adds valid access and refresh token cookies to the test client."""

        user = self.create_test_user()
        refresh = RefreshToken.for_user(user)

        self.client.cookies['access_token'] = str(refresh.access_token)
        self.client.cookies['refresh_token'] = str(refresh)

        return refresh
