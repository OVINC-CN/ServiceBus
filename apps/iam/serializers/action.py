from django.utils.translation import gettext_lazy
from rest_framework import serializers

from apps.iam.models import Action


class ActionInfoSerializer(serializers.ModelSerializer):
    """
    Action Info
    """

    class Meta:
        model = Action
        fields = "__all__"


class ActionListRequestSerializer(serializers.Serializer):
    """
    Action List
    """

    application_id = serializers.CharField(label=gettext_lazy("Application ID"))


class ActionCreateSerializer(serializers.ModelSerializer):
    """
    Create Action
    """

    class Meta:
        model = Action
        fields = "__all__"


class ActionUpdateSerializer(serializers.ModelSerializer):
    """
    Update Action
    """

    class Meta:
        model = Action
        fields = ["action_name", "resource_id", "resource_name", "description"]


class ActionListAllRequestSerializer(serializers.Serializer):
    """
    Action List All
    """

    application_id = serializers.CharField(label=gettext_lazy("Application ID"))
