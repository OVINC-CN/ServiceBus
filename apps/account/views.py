from django.conf import settings
from django.http import HttpResponseRedirect

from core.auth import SessionAuthenticate
from core.viewsets import MainViewSet


class AdminLoginViewSet(MainViewSet):
    """登入跳转"""

    authentication_classes = [SessionAuthenticate]

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(settings.FRONTEND_URL)


class AdminLogoutViewSet(MainViewSet):
    """登出跳转"""

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(settings.FRONTEND_URL)
