"""Tests for the user registration API endpoint."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.tests.mixins import AuthTestMixin


class RegistrationApiTests(AuthTestMixin, APITestCase):
    """Tests registration endpoint behavior."""

    def test_registration_creates_user_without_authentication(self):
        """Ensures unauthenticated users can register with valid data."""

        response = self.client.post(
            self.get_register_url(),
            self.get_valid_registration_data(),
            format='json',
        )

        user = get_user_model().objects.get(username='new_user')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'User created successfully!')
        self.assertEqual(self.get_user_count(), 1)
        self.assertEqual(user.email, 'new_user@example.com')
        self.assertTrue(user.check_password('SecurePass123!'))


    def test_registration_fails_when_passwords_do_not_match(self):
        """Ensures mismatching passwords are rejected."""

        data = self.get_valid_registration_data()
        data['confirmed_password'] = 'DifferentPass123!'

        response = self.client.post(
            self.get_register_url(),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.get_user_count(), 0)


    def test_registration_fails_when_username_already_exists(self):
        """Ensures duplicate usernames are rejected."""

        self.create_test_user()
        data = self.get_valid_registration_data()
        data['username'] = 'test_user'

        response = self.client.post(
            self.get_register_url(),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.get_user_count(), 1)


    def test_registration_fails_when_email_already_exists(self):
        """Ensures duplicate emails are rejected."""

        self.create_test_user()
        data = self.get_valid_registration_data()
        data['email'] = 'test_user@example.com'

        response = self.client.post(
            self.get_register_url(),
            data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.get_user_count(), 1)


    def test_registration_fails_when_required_fields_are_missing(self):
        """Ensures required fields are validated."""

        required_fields = ['username', 'email', 'password', 'confirmed_password']

        for field_name in required_fields:
            data = self.get_valid_registration_data()
            data.pop(field_name)

            response = self.client.post(
                self.get_register_url(),
                data,
                format='json',
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(self.get_user_count(), 0)


    @patch('auth_app.api.views.RegistrationSerializer.save')
    def test_registration_returns_500_on_unexpected_error(self, mocked_save):
        """Ensures unexpected registration errors return status 500."""

        mocked_save.side_effect = Exception('Unexpected error')

        response = self.client.post(
            self.get_register_url(),
            self.get_valid_registration_data(),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)