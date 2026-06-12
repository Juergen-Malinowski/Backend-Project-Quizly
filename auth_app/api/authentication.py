"""Custom authentication classes for JWT cookie authentication."""

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticates users with an access token from HttpOnly cookies."""

    def authenticate(self, request):
        """Reads the access token from cookies and validates it."""

        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token