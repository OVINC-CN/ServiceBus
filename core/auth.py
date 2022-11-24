from typing import Union

from django.conf import settings
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication, SessionAuthentication

from apps.account.models import User
from core.exceptions import LoginRequired

AUTH_TOKEN_CHECK_KEY = "_auth_token_authenticated"


class SessionAuthenticate(SessionAuthentication):
    """
    Session Auth
    """

    def authenticate(self, request) -> Union[tuple, None]:
        # User Request
        user = getattr(request._request, "user", None)
        if not user or not user.is_authenticated:
            return None
        # Get Auth Token
        auth_token = request.COOKIES.get(settings.AUTH_TOKEN_NAME, None)
        if auth_token is None:
            return None
        # Verify Auth Token
        username = cache.get(auth_token)
        if username != user.username:
            return None
        setattr(user, AUTH_TOKEN_CHECK_KEY, True)
        return user, None


class AuthTokenAuthenticate(BaseAuthentication):
    """
    Auth Token Authenticate
    """

    def authenticate(self, request) -> (User, None):
        # User Auth Token
        user = getattr(request._request, "user", None)
        is_auth_token_authenticated = getattr(user, AUTH_TOKEN_CHECK_KEY, False)
        # Check Auth Status
        if is_auth_token_authenticated:
            return user, None
        raise LoginRequired()
