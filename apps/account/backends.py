from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as _ModelBackend

from apps.account.exceptions import SignInParamNotExist, UserNotExist, WrongSignInParam
from apps.account.models import User

USER_MODEL: User = get_user_model()


class ModelBackend(_ModelBackend):
    """
    Model Backend
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check Username and Password
        if not username or not password:
            raise SignInParamNotExist(SignInParamNotExist.default_detail)
        # Retrieve User
        try:
            user = USER_MODEL.objects.get(username=username)
        except USER_MODEL.DoesNotExist:
            raise UserNotExist()
        # Check Password
        if user.check_password(password):
            return user
        raise WrongSignInParam()
