from django.utils.translation import gettext_lazy
from rest_framework import status
from rest_framework.exceptions import APIException


class UploadFileFailed(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = gettext_lazy("Upload File Failed")
