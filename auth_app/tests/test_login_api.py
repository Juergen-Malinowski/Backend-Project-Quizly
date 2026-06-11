"""Tests for the user login API endpoint."""

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.mixins import AuthTestMixin


class LoginApiTests(AuthTestMixin, APITestCase):
    """Tests login endpoint behavior."""

    def test_login_returns_user_and_sets_cookies_without_authentication(self):
        """Ensures unauthenticated users can log in with valid data."""

        user = self.create_test_user()

        response = self.client.post(
            self.get_login_url(),
            self.get_valid_login_data(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {'detail', 'user'})
        self.assertEqual(response.data['detail'], 'Login successfully!')
        self.assertEqual(set(response.data['user'].keys()),{'id', 'username', 'email'})
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(response.data['user']['username'], user.username)
        self.assertEqual(response.data['user']['email'], user.email)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])


    def test_login_fails_with_invalid_password(self):
        """Ensures invalid credentials are rejected."""

        self.create_test_user()
        data = self.get_valid_login_data()
        data['password'] = 'WrongPass123!'

        response = self.client.post(
            self.get_login_url(),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access_token', response.cookies)
        self.assertNotIn('refresh_token', response.cookies)


    def test_login_fails_with_unknown_username(self):
        """Ensures unknown users are rejected."""

        data = self.get_valid_login_data()
        data['username'] = 'unknown_user'

        response = self.client.post(
            self.get_login_url(),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access_token', response.cookies)
        self.assertNotIn('refresh_token', response.cookies)


    def test_login_error_message_is_general(self):
        """Ensures invalid login feedback does not reveal credential details."""

        response = self.client.post(
            self.get_login_url(),
            self.get_valid_login_data(),
            format='json',
        )

        error_text = str(response.data.get('detail', '')).lower()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertTrue(response.data['detail'])
        self.assertNotIn('password', error_text)
        self.assertNotIn('username', error_text)
        self.assertNotIn('user does not exist', error_text)
        self.assertNotIn('not found', error_text)


    def test_login_fails_when_required_fields_are_missing(self):
        """Ensures required login fields are validated."""

        required_fields = ['username', 'password']

        for field_name in required_fields:
            data = self.get_valid_login_data()
            data.pop(field_name)

            response = self.client.post(
                self.get_login_url(),
                data,
                format='json',
            )

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertNotIn('access_token', response.cookies)
            self.assertNotIn('refresh_token', response.cookies)


    @patch('auth_app.api.views.LoginSerializer.validate')
    def test_login_returns_500_on_unexpected_error(self, mocked_validate):
        """Ensures unexpected login errors return status 500."""

        mocked_validate.side_effect = Exception('Unexpected error')

        response = self.client.post(
            self.get_login_url(),
            self.get_valid_login_data(),
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )