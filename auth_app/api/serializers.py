"""Serializers for authentication API endpoints."""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates registration data and creates a new user."""

    confirmed_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        """Defines serializer fields for user registration."""

        model = get_user_model()
        fields = [
            'username',
            'email',
            'password',
            'confirmed_password',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }


    def validate_username(self, value):
        """Ensures the username is not already used."""

        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')

        return value


    def validate_email(self, value):
        """Ensures the email address is not already used."""

        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')

        return value


    def validate(self, attrs):
        """Ensures passwords match and password rules are valid."""

        password = attrs.get('password')
        confirmed_password = attrs.get('confirmed_password')

        if password != confirmed_password:
            raise serializers.ValidationError('Passwords do not match.')

        validate_password(password)

        return attrs


    def create(self, validated_data):
        """Creates a user with a hashed password."""

        validated_data.pop('confirmed_password')

        return get_user_model().objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validates login credentials and returns the authenticated user."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Authenticates the user with username and password."""

        user = authenticate(
            username=attrs.get('username'),
            password=attrs.get('password'),
        )

        if not user:
            raise serializers.ValidationError('Invalid credentials.')

        attrs['user'] = user

        return attrs