from rest_framework.decorators import action
from rest_framework.response import Response

from apps.iam.models import Instance
from apps.iam.permissions import IAMActionAppPermission, IAMActionObjAppPermission
from apps.iam.serializers import (
    InstanceCreateSerializer,
    InstanceListRequestSerializer,
    InstanceSerializer,
    InstanceUpdateSerializer,
)
from apps.iam.serializers.instance import InstanceAllSerializer
from core.auth import ApplicationAuthenticate
from core.constants import ViewActionChoices
from core.viewsets import CreateMixin, DestroyMixin, ListMixin, MainViewSet, UpdateMixin


class IAMInstanceViewSet(ListMixin, MainViewSet):
    """
    IAM Instance
    """

    queryset = Instance.get_queryset()
    serializer_class = InstanceSerializer

    def list(self, request, *args, **kwargs):
        """
        Instance List
        """

        # validate request
        request_serializer = InstanceListRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        # pagination
        queryset = (
            Instance.get_queryset()
            .filter(action_id=request_serializer.validated_data["action_id"])
            .order_by("instance_id")
        )
        page = self.paginate_queryset(queryset)

        # data serialize
        serializer = InstanceSerializer(page, many=True)
        data = serializer.data

        # response
        return self.get_paginated_response(data)

    @action(methods=["GET"], detail=False)
    def all(self, request, *args, **kwargs):
        """
        All Instance
        """

        # validate request
        request_serializer = InstanceListRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)

        # queryset
        queryset = (
            Instance.get_queryset()
            .filter(action_id=request_serializer.validated_data["action_id"])
            .order_by("instance_id")
        )

        # response
        serializer = InstanceAllSerializer(queryset, many=True)
        return Response(serializer.data)


class IAMInstanceAppViewSet(CreateMixin, UpdateMixin, DestroyMixin, MainViewSet):
    """
    IAM Instance
    """

    queryset = Instance.get_queryset()
    serializer_class = InstanceSerializer
    authentication_classes = [ApplicationAuthenticate]

    def get_permissions(self):
        if self.action in [ViewActionChoices.CREATE]:
            return [IAMActionAppPermission()]
        if self.action in [ViewActionChoices.UPDATE, ViewActionChoices.PARTIAL_UPDATE, ViewActionChoices.DESTROY]:
            return [IAMActionObjAppPermission()]
        return []

    def create(self, request, *args, **kwargs):
        """
        create instance
        """

        # validate request
        request_serializer = InstanceCreateSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        # save
        request_serializer.save()

        # response
        return Response()

    def update(self, request, *args, **kwargs):
        """
        update instance
        """

        # get instance
        instance = self.get_object()

        # validate request
        request_serializer = InstanceUpdateSerializer(instance, data=request.data, partial=True)
        request_serializer.is_valid(raise_exception=True)

        # save
        instance = request_serializer.save()

        # response
        return Response(InstanceSerializer(instance).data)
