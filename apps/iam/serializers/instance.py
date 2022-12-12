from django.utils.translation import gettext_lazy
from rest_framework import serializers

from apps.iam.models import Instance


class InstanceSerializer(serializers.ModelSerializer):
    """
    Instance Info
    """

    class Meta:
        model = Instance
        fields = "__all__"


class InstanceAllSerializer(serializers.ModelSerializer):
    """
    Instance Simple Info
    """

    class Meta:
        model = Instance
        fields = ["id", "instance_id", "instance_name"]


class InstanceListRequestSerializer(serializers.Serializer):
    """
    Instance List
    """

    action_id = serializers.CharField(label=gettext_lazy("Action ID"))


class InstanceCreateSerializer(serializers.ModelSerializer):
    """
    Create Instance
    """

    class Meta:
        model = Instance
        fields = "__all__"


class InstanceUpdateSerializer(serializers.ModelSerializer):
    """
    Update Instance
    """

    class Meta:
        model = Instance
        fields = ["instance_name"]


class BulkInstanceSerializer(serializers.Serializer):
    """
    Bulk Save Instance
    """

    id = serializers.CharField(label=gettext_lazy("ID"), required=False)
    action_id = serializers.CharField(label=gettext_lazy("Action"))
    instance_id = serializers.CharField(label=gettext_lazy("Instance ID"))
    instance_name = serializers.CharField(label=gettext_lazy("Instance Name"))
