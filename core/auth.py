import json
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext
from rest_framework.authentication import BaseAuthentication, SessionAuthentication

from apps.application.models import Application
from core.constants import APP_AUTH_HEADER_KEY, APP_AUTH_ID_KEY, APP_AUTH_SECRET_KEY
from core.exceptions import AppAuthFailed, LoginRequired

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


class ApplicationAuthenticate(BaseAuthentication):
    """
    Application Authenticate
    """

    def authenticate(self, request) -> (Application, None):
        # get app params
        app_params = json.loads(request.META.get(APP_AUTH_HEADER_KEY, "{}"))
        if not isinstance(app_params, dict):
            raise AppAuthFailed(gettext("App Auth Params is not Json"))
        app_code = app_params.get(APP_AUTH_ID_KEY)
        app_secret = app_params.get(APP_AUTH_SECRET_KEY)
        if not app_code or not app_secret:
            raise AppAuthFailed(gettext("App Auth Params Not Exist"))
        # varify app
        try:
            app = Application.objects.get(app_code=app_code)
        except Application.DoesNotExist:
            raise AppAuthFailed(gettext("App Not Exist"))
        # verify secret
        if app.check_secret(app_secret):
            return app, None
        raise AppAuthFailed(gettext("App Code or Secret Incorrect"))
