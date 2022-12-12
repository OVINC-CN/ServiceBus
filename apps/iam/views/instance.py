from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.iam.models import Instance
from apps.iam.permissions import (
    BulkSaveInstancePermission,
    IAMActionAppPermission,
    IAMActionObjAppPermission,
)
from apps.iam.serializers import (
    BulkInstanceSerializer,
    InstanceAllSerializer,
    InstanceCreateSerializer,
    InstanceListRequestSerializer,
    InstanceSerializer,
    InstanceUpdateSerializer,
)
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
        if self.action in ["bulk_save"]:
            return [BulkSaveInstancePermission()]
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

    @action(methods=["POST"], detail=False)
    def bulk_save(self, request, *args, **kwargs):
        """
        bulk create or update instance
        """

        # validate_request
        request_serializer = BulkInstanceSerializer(data=request.data, many=True)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # save
        data = self._bulk_save(request_data)

        # response
        serializer = InstanceSerializer(instance=data, many=True)
        return Response(serializer.data)

    @transaction.atomic()
    def _bulk_save(self, data: list) -> list:
        """
        bulk create
        """

        # init response
        result = []

        # split data
        to_update = {}
        to_create = []
        for instance in data:
            if instance.get("id"):
                to_update[instance["id"]] = instance
            else:
                to_create.append(instance)

        # do create
        if to_create:
            result.extend(
                Instance.objects.bulk_create(
                    [
                        Instance(
                            action_id=_instance["action_id"],
                            instance_id=_instance["instance_id"],
                            instance_name=_instance["instance_name"],
                        )
                        for _instance in to_create
                    ]
                )
            )

        # do update
        if to_update:
            db_instances = Instance.objects.filter(id__in=to_update.keys())
            for _instance in db_instances:
                for _key, _val in to_update[_instance.id].items():
                    setattr(_instance, _key, _val)
            Instance.objects.bulk_update(db_instances, fields=["instance_id", "instance_name"])
            result.extend(db_instances)

        return result
