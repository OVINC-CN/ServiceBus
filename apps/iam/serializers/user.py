from typing import List

from django.utils.translation import gettext_lazy
from rest_framework import serializers

from apps.iam.models import Instance, UserPermission
from apps.iam.serializers import InstanceSerializer


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
        attrs["instances"] = Instance.objects.filter(pk__in=attrs["instances"], action=attrs["action"]).values_list(
            "id", flat=True
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
                Instance.objects.filter(pk__in=attrs["instances"], action=self.instance.action).values_list(
                    "id", flat=True
                )
            )
        return attrs
