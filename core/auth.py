from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication, SessionAuthentication

from core.exceptions import LoginRequired

AUTH_TOKEN_CHECK_KEY = "_auth_token_authenticated"
USER_MODEL = get_user_model()


class SessionAuthenticate(SessionAuthentication):
    """
    Session Auth
    """

    def authenticate(self, request) -> Union[tuple, None]:
        # Get Auth Token
        auth_token = request.COOKIES.get(settings.AUTH_TOKEN_NAME, None)
        if not auth_token:
            return None
        # Verify Auth Token
        username = cache.get(auth_token)
        if not username:
            return None
        # Get User
        try:
            user = USER_MODEL.objects.get(username=username)
        except USER_MODEL.DoesNotExist:
            return None
        setattr(user, AUTH_TOKEN_CHECK_KEY, True)
        return user, None


class AuthTokenAuthenticate(BaseAuthentication):
    """
    Auth Token Authenticate
    """

    def authenticate(self, request) -> (USER_MODEL, None):
        # User Auth Token
        user = getattr(request._request, "user", None)
        is_auth_token_authenticated = getattr(user, AUTH_TOKEN_CHECK_KEY, False)
        # Check Auth Status
        if is_auth_token_authenticated:
            return user, None
        raise LoginRequired()
