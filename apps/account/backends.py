from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.backends import ModelBackend as _ModelBackend
from django.core.cache import cache

from apps.account.models import User

USER_MODEL: User = get_user_model()


class ModelBackend(_ModelBackend):
    """
    Model Backend
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check Username and Password
        if not username:
            username = kwargs.get(USER_MODEL.USERNAME_FIELD)
        if not username and not password:
            return None
        # Retrieve User
        try:
            user = USER_MODEL.objects.get(username=username)
        except USER_MODEL.DoesNotExist:
            return None
        # Check Password
        if user.check_password(password):
            return user


class TokenBackend(BaseBackend):
    """
    Token Backend
    """

    def authenticate(self, request, token=None, **kwargs):
        # Check Token Exist
        if not token:
            return None
        # Retrieve Username
        username = cache.get(token)
        if not username:
            return None
        # Retrieve User
        try:
            return USER_MODEL.objects.get(username=username)
        except USER_MODEL.DoesNotExist:
            return None
