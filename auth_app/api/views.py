"""Views for authentication API endpoints."""


from rest_framework.views import APIView


class RegistrationView(APIView):
    """Handles user registration."""
    pass


class LoginView(APIView):
    """Handles user login."""
    pass


class LogoutView(APIView):
    """Handles user logout."""
    pass


class TokenRefreshView(APIView):
    """Handles access token refresh."""
    pass
