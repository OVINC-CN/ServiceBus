from typing import List

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.iam.constants import PermissionStatusChoices
from apps.iam.models import Action, Instance, UserPermission, UserPermissionSnapshot
from apps.iam.permissions import ManagePermissionPermission, UserPermissionSelf
from apps.iam.serializers import (
    ApplyPermissionSerializer,
    AuthPermissionSerializer,
    CheckPermissionSerializer,
    ManagePermissionApplySerializer,
    ManagePermissionSerializer,
    PermissionItemSerializer,
    UpdatePermissionSerializer,
    UserPermissionListRequestSerializer,
    UserPermissionListSerializer,
    UserPermissionSerializer,
)
from apps.iam.utils import sync_snapshot, update_snapshot
from core.auth import ApplicationAuthenticate
from core.constants import ViewActionChoices
from core.viewsets import CreateMixin, DestroyMixin, ListMixin, MainViewSet, UpdateMixin

USER_MODEL = get_user_model()


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
        request_serializer = UserPermissionListRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # page
        queryset = UserPermission.get_queryset().filter(
            user=request.user, action__application_id=request_data["application_id"]
        )
        if request_data["action_id"]:
            queryset = queryset.filter(action_id=request_data["action_id"])
        queryset = queryset.select_related("action").order_by("-status", "-update_at")
        page = self.paginate_queryset(queryset)

        # instance data
        instance_ids = []
        for up in page:
            instance_ids.extend(up.instances if up.instances else [])
        instances = Instance.objects.filter(pk__in=instance_ids)
        instance_map = {instance.pk: instance for instance in instances}

        # serialize
        serializer = UserPermissionListSerializer(page, many=True, context=instance_map)
        return self.get_paginated_response(serializer.data)

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

    def get_permissions(self):
        if self.action in ["auth"]:
            return []
        return [ManagePermissionPermission()]

    def list(self, request, *args, **kwargs):
        """
        List User Permission
        """

        # validate request
        request_serializer = ManagePermissionSerializer(data=request.query_params)
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
        return self.get_paginated_response(serializer.data)

    @transaction.atomic()
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
        permission = get_object_or_404(UserPermission, id=permission_id, status=PermissionStatusChoices.DEALING.value)
        permission.status = status
        permission.save(update_fields=["status"])
        if status == PermissionStatusChoices.ALLOWED.value:
            sync_snapshot([permission.id], PermissionStatusChoices.ALLOWED.value)
        elif status == PermissionStatusChoices.DENIED.value:
            sync_snapshot([permission_id], PermissionStatusChoices.DENIED.value)

        return Response()

    @transaction.atomic()
    @action(methods=["POST"], detail=False, authentication_classes=[ApplicationAuthenticate])
    def auth(self, request, *args, **kwargs):
        """
        auth permission
        """

        # validate request
        request_serializer = AuthPermissionSerializer(data=request.data, context={"application": request.user})
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # get exist permission
        permission = UserPermission.objects.filter(user=request_data["user"], action=request_data["action"]).first()

        # if exists, update
        if permission:
            permission.instances = list(set(permission.instances) | set(request_data["instances"]))
            permission.all_instances = request_data["all_instances"]
            permission.save(update_fields=["instances", "all_instances", "update_at"])
            update_snapshot(permission.id, request_data["instances"], request_data["all_instances"])
        # if not exists, create and set allowed
        else:
            permission = UserPermission.objects.create(
                user=request_data["user"],
                action=request_data["action"],
                instances=request_data["instances"],
                all_instances=request_data["all_instances"],
                status=PermissionStatusChoices.ALLOWED,
            )
            sync_snapshot([permission.id], PermissionStatusChoices.ALLOWED.value)

        # response
        serializer = UserPermissionSerializer(permission)
        return Response(serializer.data)


class CheckPermissionViewSet(CreateMixin, MainViewSet):
    """
    Check Permission
    """

    queryset = UserPermission.get_queryset()
    serializer_class = UserPermissionSerializer

    def create(self, request, *args, **kwargs):
        """
        check user permission
        """

        # validate request
        request_serializer = PermissionItemSerializer(data=request.data, many=True)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        # check
        return self._check(request.user.username, data)

    @action(methods=["POST"], detail=False, authentication_classes=[ApplicationAuthenticate])
    def api(self, request, *args, **kwargs):
        """
        check permission api
        """

        # validate request
        request_serializer = CheckPermissionSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data

        # check
        return self._check(data["username"], data["permissions"])

    def _check(self, username, check_permissions: List[dict]) -> Response:
        """
        check permission
        """

        # load permission
        action_ids = [p["action"] for p in check_permissions]
        allowed_permissions_map = {
            p.action_id: p
            for p in UserPermissionSnapshot.objects.filter(
                user_id=username, action_id__in=action_ids, status=PermissionStatusChoices.ALLOWED
            )
        }

        # check permission
        for p in check_permissions:
            allowed_permission: UserPermissionSnapshot = allowed_permissions_map.get(p["action"])
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
        return Response({"username": username, "permissions": check_permissions})

    @action(methods=["GET"], detail=False)
    def is_superuser(self, request, *args, **kwargs):
        """
        check user is superuser
        """

        return Response({"is_superuser": request.user.is_superuser})
