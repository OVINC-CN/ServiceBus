from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class ActionDoesNotExist(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = gettext_lazy("Action Not Exist")
