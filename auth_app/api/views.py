"""Views for authentication API endpoints."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer
from auth_app.api.utils import (
    delete_auth_cookies,
    get_login_response_data,
    set_access_cookie,
    set_auth_cookies,
)


class RegistrationView(APIView):
    """Handles user registration."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Creates a new user account."""

        try:
            serializer = RegistrationSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'detail': 'User created successfully!'},
                    status=status.HTTP_201_CREATED,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(APIView):
    """Handles user login."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticates a user and sets JWT cookies."""

        try:
            serializer = LoginSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {'detail': 'Invalid credentials.'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            data = get_login_response_data(user)
            response = Response(data, status=status.HTTP_200_OK)
            set_auth_cookies(response, refresh)

            return response

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    """Handles user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklists the refresh token and deletes auth cookies."""

        try:
            refresh_token = request.COOKIES.get('refresh_token')
            RefreshToken(refresh_token).blacklist()
            response = Response(
                {
                    'detail': (
                        'Log-Out successfully! All Tokens will be deleted. '
                        'Refresh token is now invalid.'
                    ),
                },
                status=status.HTTP_200_OK,
            )

            delete_auth_cookies(response)

            return response

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TokenRefreshView(APIView):
    """Handles access token refresh."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Creates a new access token from the refresh cookie."""

        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            response = Response(
                {'detail': 'Token refreshed'},
                status=status.HTTP_200_OK,
            )

            set_access_cookie(response, refresh)

            return response

        except TokenError:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
