from typing import List

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy
from rest_framework import serializers

from apps.account.exceptions import UserNotExist
from apps.account.models import User
from apps.iam.constants import PermissionStatusChoices
from apps.iam.exceptions import ActionDoesNotExist
from apps.iam.models import Action, Instance, UserPermission
from apps.iam.serializers import InstanceSerializer

USER_MODEL: User = get_user_model()


class UserPermissionSerializer(serializers.ModelSerializer):
    """
    User Permission
    """

    class Meta:
        model = UserPermission
        fields = "__all__"


class UserPermissionListRequestSerializer(serializers.Serializer):
    """
    User Permission List Request
    """

    application_id = serializers.CharField(label=gettext_lazy("Application ID"))
    action_id = serializers.CharField(label=gettext_lazy("Action ID"), default="")


class UserPermissionListSerializer(serializers.ModelSerializer):
    """
    User Permission List
    """

    action_id = serializers.SerializerMethodField(label=gettext_lazy("Action ID"))
    action_name = serializers.SerializerMethodField(label=gettext_lazy("Action Name"))
    resource_name = serializers.SerializerMethodField(label=gettext_lazy("Resource Name"))
    description = serializers.SerializerMethodField(label=gettext_lazy("Description"))
    instances = serializers.SerializerMethodField(label=gettext_lazy("Instances"))

    class Meta:
        model = UserPermission
        fields = "__all__"

    def get_action_id(self, obj: UserPermission) -> str:
        return obj.action.action_id

    def get_action_name(self, obj: UserPermission) -> str:
        return obj.action.action_name

    def get_resource_name(self, obj: UserPermission) -> str:
        return obj.action.resource_name

    def get_description(self, obj: UserPermission) -> str:
        return obj.action.description

    def get_instances(self, obj: UserPermission) -> List[dict]:
        # all instances
        if obj.all_instances:
            return []
        # instance list
        instances = []
        instance_ids = obj.instances
        if not instance_ids:
            return []
        for pk in instance_ids:
            instance = self.context.get(pk)
            if not instance:
                continue
            instances.append(InstanceSerializer(instance).data)
        return instances


class ApplyPermissionSerializer(serializers.ModelSerializer):
    """
    Apply Permission
    """

    class Meta:
        model = UserPermission
        fields = "__all__"

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        attrs["instances"] = list(
            Instance.objects.filter(
                pk__in=attrs["instances"],
                application=attrs["action"].application,
                resource_id=attrs["action"].resource_id,
            ).values_list("id", flat=True)
        )
        return attrs


class UpdatePermissionSerializer(serializers.ModelSerializer):
    """
    Update Permission
    """

    class Meta:
        model = UserPermission
        fields = ["instances", "all_instances", "status"]

    def validate(self, attrs: dict) -> dict:
        attrs = super().validate(attrs)
        if attrs.get("instances"):
            attrs["instances"] = list(
                Instance.objects.filter(
                    pk__in=attrs["instances"],
                    application=self.instance.action.application,
                    resource_id=self.instance.action.resource_id,
                ).values_list("id", flat=True)
            )
        return attrs


class PermissionItemSerializer(serializers.Serializer):
    """
    Permission Item
    """

    action = serializers.CharField(label=gettext_lazy("Action ID"))
    instances = serializers.ListSerializer(
        label=gettext_lazy("Instances"), child=serializers.CharField(label=gettext_lazy("Instance ID"))
    )


class CheckPermissionSerializer(serializers.Serializer):
    """
    Check Permission
    """

    username = serializers.CharField(label=gettext_lazy("Username"), required=False)
    permissions = PermissionItemSerializer(label=gettext_lazy("Permissions"), many=True)


class ManagePermissionSerializer(serializers.Serializer):
    """
    Manage Permission
    """

    application_id = serializers.CharField(label=gettext_lazy("Application ID"))


class ManagePermissionApplySerializer(serializers.Serializer):
    """
    Manager Permission Apply
    """

    permission_id = serializers.CharField(label=gettext_lazy("Permission ID"))
    status = serializers.ChoiceField(label=gettext_lazy("Permission Status"), choices=PermissionStatusChoices.choices)


class AuthPermissionSerializer(serializers.Serializer):
    """
    Auth Permission
    """

    user = serializers.CharField(label=gettext_lazy("User"))
    action = serializers.CharField(label=gettext_lazy("Action"))
    instances = serializers.ListField(
        label=gettext_lazy("Instances"), child=serializers.CharField(label=gettext_lazy("Instance ID"))
    )
    all_instances = serializers.BooleanField(label=gettext_lazy("All Instances"))

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        data["instances"] = list(
            Instance.objects.filter(
                application=attrs["action"].application,
                resource_id=attrs["action"].resource_id,
                id__in=data["instances"],
            ).values_list("id", flat=True)
        )
        return data

    def validate_user(self, user: str) -> USER_MODEL:
        try:
            return USER_MODEL.objects.get(username=user)
        except USER_MODEL.DoesNotExist:
            raise serializers.ValidationError(str(UserNotExist.default_detail))

    def validate_action(self, action: str) -> Action:
        try:
            return Action.objects.get(id=action, application=self.context["application"])
        except Action.DoesNotExist:
            raise serializers.ValidationError(str(ActionDoesNotExist.default_detail))
