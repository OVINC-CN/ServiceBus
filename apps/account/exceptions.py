from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class SignInParamNotExist(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Sign In Params Not Exist")


class UserNotExist(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = gettext_lazy("User Not Exist")


class WrongSignInParam(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Wrong Username or Password")


class TokenNotExist(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Token Not Exist")


class WrongToken(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = gettext_lazy("Wrong Token")
