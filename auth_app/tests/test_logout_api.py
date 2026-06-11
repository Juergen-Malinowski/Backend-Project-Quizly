"""Tests for the user logout API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from auth_app.tests.mixins import AuthTestMixin


class LogoutApiTests(AuthTestMixin, APITestCase):
    """Tests logout endpoint behavior."""

    def test_logout_deletes_cookies_and_blacklists_refresh_token(self):
        """Ensures authenticated users can log out successfully."""

        refresh = self.authenticate_with_cookie_tokens()

        response = self.client.post(
            self.get_logout_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['detail'],
            'Log-Out successfully! All Tokens will be deleted. '
            'Refresh token is now invalid.',
        )
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertEqual(response.cookies['access_token']['max-age'], 0)
        self.assertEqual(response.cookies['refresh_token']['max-age'], 0)
        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=refresh['jti'],
            ).exists(),
        )


    def test_logout_fails_without_authentication(self):
        """Ensures unauthenticated users cannot log out."""

        response = self.client.post(
            self.get_logout_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    @patch('auth_app.api.views.RefreshToken')
    def test_logout_returns_500_on_unexpected_error(self, mocked_token):
        """Ensures unexpected logout errors return status 500."""

        self.authenticate_with_cookie_tokens()
        mocked_token.side_effect = Exception('Unexpected error')

        response = self.client.post(
            self.get_logout_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)