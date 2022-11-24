from rest_framework.response import Response

from apps.account.models import User
from core.auth import SessionAuthenticate
from core.viewsets import MainViewSet


class HomeView(MainViewSet):
    """
    Home View
    """

    queryset = User.get_queryset()
    authentication_classes = [SessionAuthenticate]

    def response(self, request):
        msg = f"[{request.method}] Connect Success"
        return Response({"resp": msg, "user": request.user.username})

    def list(self, request, *args, **kwargs):
        return self.response(request)

    def create(self, request, *args, **kwargs):
        return self.response(request)

    def update(self, request, *args, **kwargs):
        return self.response(request)

    def destroy(self, request, *args, **kwargs):
        return self.response(request)
