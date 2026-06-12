"""Views for authentication API endpoints."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import RegistrationSerializer


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
    pass


class LogoutView(APIView):
    """Handles user logout."""
    pass


class TokenRefreshView(APIView):
    """Handles access token refresh."""
    pass
