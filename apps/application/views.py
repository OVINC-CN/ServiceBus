from collections import defaultdict

from django.contrib.auth import get_user_model
from rest_framework.response import Response

from apps.account.models import User
from apps.application.models import Application, ApplicationManager
from apps.application.permissions import (
    ApplicationAdminPermission,
    ApplicationManagePermission,
)
from apps.application.serializers import (
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationSerializer,
    ApplicationUpdateRequestSerializer,
    ApplicationUpdateResponseSerializer,
)
from core.constants import ViewActionChoices
from core.viewsets import CreateMixin, DestroyMixin, ListMixin, MainViewSet, UpdateMixin

USER_MODEL: User = get_user_model()


class ApplicationViewSet(ListMixin, CreateMixin, UpdateMixin, DestroyMixin, MainViewSet):
    """
    Application
    """

    queryset = Application.get_queryset()
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.action in [ViewActionChoices.LIST]:
            return []
        if self.action in [ViewActionChoices.UPDATE, ViewActionChoices.PARTIAL_UPDATE]:
            return [ApplicationManagePermission()]
        return [ApplicationAdminPermission()]

    def list(self, request, *args, **kwargs):
        """
        Application List
        """

        # pagination
        page = self.paginate_queryset(self.queryset)

        # manager info
        manager_map = defaultdict(list)
        app_managers = ApplicationManager.objects.filter(application__in=page).select_related("manager")
        for app_manager in app_managers:
            manager_map[app_manager.application_id].append(app_manager.manager)

        # data serialize
        serializer = ApplicationListSerializer(page, many=True, context=manager_map)
        data = serializer.data

        # response
        return self.get_paginated_response(data)

    def create(self, request, *args, **kwargs):
        """
        Create Application
        """

        # validate request
        request_serializer = ApplicationCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        # create
        request_serializer.save()

        # response
        return Response()

    def update(self, request, *args, **kwargs):
        """
        Update Application
        """

        # get instance
        instance = self.get_object()

        # validate request
        request_serializer = ApplicationUpdateRequestSerializer(instance, data=request.data, partial=True)
        request_serializer.is_valid(raise_exception=True)

        # update
        instance = request_serializer.save()

        # response
        serializer = ApplicationUpdateResponseSerializer(instance)
        return Response(serializer.data)
