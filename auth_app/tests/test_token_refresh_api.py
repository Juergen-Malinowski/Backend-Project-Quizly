"""Tests for the token refresh API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.mixins import AuthTestMixin


class TokenRefreshApiTests(AuthTestMixin, APITestCase):
    """Tests token refresh endpoint behavior."""

    def test_token_refresh_sets_new_access_token_cookie(self):
        """Ensures refresh cookie authentication creates a new access cookie."""

        self.authenticate_with_cookie_tokens()
        old_access_token = self.client.cookies['access_token'].value

        response = self.client.post(
            self.get_token_refresh_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Token refreshed')
        self.assertIn('access_token', response.cookies)

        new_access_token = response.cookies['access_token'].value
        self.assertNotEqual(new_access_token, old_access_token)
        self.assertTrue(response.cookies['access_token']['httponly'])


    def test_token_refresh_fails_without_refresh_token_cookie(self):
        """Ensures refresh fails when the refresh cookie is missing."""

        self.assertNotIn('refresh_token', self.client.cookies)

        response = self.client.post(
            self.get_token_refresh_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access_token', response.cookies)


    def test_token_refresh_fails_with_invalid_refresh_token_cookie(self):
        """Ensures refresh fails when the refresh cookie is invalid."""

        self.client.cookies['refresh_token'] = 'invalid-refresh-token'

        self.assertEqual(self.client.cookies['refresh_token'].value, 'invalid-refresh-token')

        response = self.client.post(
            self.get_token_refresh_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access_token', response.cookies)


    @patch('auth_app.api.views.RefreshToken')
    def test_token_refresh_returns_500_on_unexpected_error(self, mocked_token):
        """Ensures unexpected token refresh errors return status 500."""

        self.authenticate_with_cookie_tokens()
        mocked_token.side_effect = Exception('Unexpected error')

        response = self.client.post(
            self.get_token_refresh_url(),
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)