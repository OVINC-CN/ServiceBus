from rest_framework.decorators import action
from rest_framework.response import Response

from apps.iam.models import Action
from apps.iam.permissions import IAMCreatePermission, IAMUpdatePermission
from apps.iam.serializers import (
    ActionCreateSerializer,
    ActionInfoSerializer,
    ActionListAllRequestSerializer,
    ActionListRequestSerializer,
    ActionUpdateSerializer,
)
from core.constants import ViewActionChoices
from core.viewsets import (
    CreateMixin,
    DestroyMixin,
    ListMixin,
    MainViewSet,
    RetrieveMixin,
    UpdateMixin,
)


class IAMActionViewSet(RetrieveMixin, ListMixin, CreateMixin, UpdateMixin, DestroyMixin, MainViewSet):
    """
    IAM Action
    """

    queryset = Action.get_queryset()
    serializer_class = ActionInfoSerializer

    def get_permissions(self):
        if self.action in [ViewActionChoices.CREATE]:
            return [IAMCreatePermission()]
        if self.action in [ViewActionChoices.UPDATE, ViewActionChoices.PARTIAL_UPDATE, ViewActionChoices.DESTROY]:
            return [IAMUpdatePermission()]
        return []

    def list(self, request, *args, **kwargs):
        """
        action list
        """

        # validate request
        request_serializer = ActionListRequestSerializer(data=request.GET)
        request_serializer.is_valid(raise_exception=True)

        # pagination
        queryset = Action.get_queryset().filter(
            application_id=request_serializer.validated_data["application_id"]
        ).order_by("action_id")
        page = self.paginate_queryset(queryset)

        # data serialize
        serializer = ActionInfoSerializer(page, many=True)
        data = serializer.data

        # response
        return self.get_paginated_response(data)

    def create(self, request, *args, **kwargs):
        """
        create action
        """

        # validate request
        request_serializer = ActionCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        # create action
        request_serializer.save()

        # response
        return Response()

    def update(self, request, *args, **kwargs):
        """
        update action
        """

        # get obj
        instance = self.get_object()

        # validate request
        request_serializer = ActionUpdateSerializer(instance=instance, data=request.data, partial=True)
        request_serializer.is_valid(raise_exception=True)

        # save
        instance = request_serializer.save()

        # response
        return Response(ActionInfoSerializer(instance).data)

    @action(methods=["GET"], detail=False)
    def all(self, request, *args, **kwargs):
        """
        action list
        """

        # validate request
        request_serializer = ActionListAllRequestSerializer(data=request.GET)
        request_serializer.is_valid(raise_exception=True)

        # response
        queryset = Action.get_queryset().filter(application_id=request_serializer.validated_data["application_id"])
        return Response(ActionInfoSerializer(queryset, many=True).data)
