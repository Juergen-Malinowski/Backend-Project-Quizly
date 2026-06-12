"""Utility functions for authentication API endpoints."""


def get_login_response_data(user):
    """Returns the documented login response payload."""

    return {
        'detail': 'Login successfully!',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
    }


def set_auth_cookies(response, refresh):
    """Sets access and refresh tokens as HttpOnly cookies."""

    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
    )

    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
    )


def delete_auth_cookies(response):
    """Deletes access and refresh token cookies."""

    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')