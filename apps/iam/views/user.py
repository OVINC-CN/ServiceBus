from rest_framework.response import Response

from apps.iam.constants import PermissionStatusChoices
from apps.iam.models import Action, Instance, UserPermission
from apps.iam.permissions import ManagePermissionPermission, UserPermissionSelf
from apps.iam.serializers import (
    ApplyPermissionSerializer,
    CheckPermissionSerializer,
    ManagePermissionApplySerializer,
    ManagePermissionSerializer,
    UpdatePermissionSerializer,
    UserPermissionListRequestSerializer,
    UserPermissionListSerializer,
    UserPermissionSerializer,
)
from core.auth import ApplicationAuthenticate
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


class ManagerUserPermissionViewSet(ListMixin, CreateMixin, MainViewSet):
    """
    Manage User Permission
    """

    queryset = UserPermission.get_queryset()
    serializer_class = UserPermissionSerializer
    permission_classes = [ManagePermissionPermission]

    def list(self, request, *args, **kwargs):
        """
        List User Permission
        """

        # validate request
        request_serializer = ManagePermissionSerializer(data=request.GET)
        request_serializer.is_valid(raise_exception=True)
        application_id = request_serializer.validated_data["application_id"]

        # load data
        action_ids = Action.objects.filter(application_id=application_id).values_list("id", flat=True)
        user_permissions = (
            UserPermission.objects.filter(action_id__in=action_ids)
            .select_related("action")
            .order_by("-status", "-update_at")
        )

        # page
        page = self.paginate_queryset(user_permissions)

        # instance data
        instance_ids = []
        for up in page:
            instance_ids.extend(up.instances if up.instances else [])
        instances = Instance.objects.filter(pk__in=instance_ids)
        instance_map = {instance.pk: instance for instance in instances}

        # response
        serializer = UserPermissionListSerializer(page, many=True, context=instance_map)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        deal apply
        """

        # validate request
        request_serializer = ManagePermissionApplySerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        permission_id = request_serializer.validated_data["permission_id"]
        status = request_serializer.validated_data["status"]

        # save
        queryset = UserPermission.objects.filter(id=permission_id, status=PermissionStatusChoices.DEALING)
        if status == PermissionStatusChoices.ALLOWED.value:
            queryset.update(status=status)
        elif status == PermissionStatusChoices.DENIED.value:
            queryset.delete()

        return Response()


class CheckPermissionViewSet(CreateMixin, MainViewSet):
    """
    Check Permission
    """

    queryset = UserPermission.get_queryset()
    serializer_class = UserPermissionSerializer
    authentication_classes = [ApplicationAuthenticate]

    def create(self, request, *args, **kwargs):
        """
        check user permission
        """

        # validate request
        request_serializer = CheckPermissionSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        username = request_serializer.validated_data["username"]
        check_permissions = request_serializer.validated_data["permissions"]

        # load permission
        action_ids = [p["action"] for p in check_permissions]
        allowed_permissions_map = {
            p.action_id: p
            for p in UserPermission.objects.filter(
                user_id=username, action_id__in=action_ids, status=PermissionStatusChoices.ALLOWED
            )
        }

        # check permission
        for p in check_permissions:
            allowed_permission: UserPermission = allowed_permissions_map.get(p["action"])
            # none match
            if not allowed_permission:
                p["is_allowed"] = False
                p["apply_instances"] = p["instances"]
                continue
            # match permission, check allow all
            if allowed_permission.all_instances:
                p["is_allowed"] = True
                p["apply_instances"] = []
                continue
            # match permission, check instances
            p["apply_instances"] = list(set(p["instances"]) - set(allowed_permission.instances))
            p["is_allowed"] = not bool(p["apply_instances"])

        # response
        return Response(request_serializer.validated_data)
