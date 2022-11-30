from rest_framework.response import Response

from apps.iam.constants import PermissionStatusChoices
from apps.iam.models import Instance, UserPermission
from apps.iam.permissions import UserPermissionSelf
from apps.iam.serializers import (
    ApplyPermissionSerializer,
    UpdatePermissionSerializer,
    UserPermissionListRequestSerializer,
    UserPermissionListSerializer,
    UserPermissionSerializer,
)
from core.constants import ViewActionChoices
from core.viewsets import CreateMixin, DestroyMixin, ListMixin, MainViewSet, UpdateMixin


class UserPermissionViewSet(ListMixin, CreateMixin, UpdateMixin, DestroyMixin, MainViewSet):
    """
    User Permission
    """

    queryset = UserPermission.get_queryset()
    serializer_class = UserPermissionSerializer

    def get_permissions(self):
        if self.action in [ViewActionChoices.UPDATE, ViewActionChoices.PARTIAL_UPDATE, ViewActionChoices.DESTROY]:
            return [UserPermissionSelf()]
        return []

    def list(self, request, *args, **kwargs):
        """
        current user permission list
        """

        # validate request
        request_serializer = UserPermissionListRequestSerializer(data=request.GET)
        request_serializer.is_valid(raise_exception=True)

        # page
        queryset = self.queryset.filter(
            user=request.user, action__application_id=request_serializer.validated_data["application_id"]
        ).select_related("action")
        page = self.paginate_queryset(queryset)

        # instance data
        instance_ids = []
        for up in page:
            instance_ids.extend(up.instances if up.instances else [])
        instances = Instance.objects.filter(pk__in=instance_ids)
        instance_map = {instance.pk: instance for instance in instances}

        # serialize
        serializer = UserPermissionListSerializer(page, many=True, context=instance_map)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        apply permission
        """

        # validate request
        request_data = request.data
        request_data["user"] = request.user
        request_data["status"] = PermissionStatusChoices.DEALING
        request_serializer = ApplyPermissionSerializer(data=request_data)
        request_serializer.is_valid(raise_exception=True)

        # save
        request_serializer.save()

        return Response()

    def update(self, request, *args, **kwargs):
        """
        update permission
        """

        # get obj
        instance = self.get_object()

        # validate request
        request_data = request.data
        request_data["status"] = PermissionStatusChoices.DEALING
        request_serializer = UpdatePermissionSerializer(instance, data=request_data, partial=True)
        request_serializer.is_valid(raise_exception=True)

        # save
        instance = request_serializer.save()

        # instance data
        if instance.instances:
            instances = Instance.objects.filter(pk__in=instance.instances)
            instance_map = {instance.pk: instance for instance in instances}
        else:
            instance_map = {}

        # serialize
        serializer = UserPermissionListSerializer(instance, context=instance_map)
        return Response(serializer.data)
