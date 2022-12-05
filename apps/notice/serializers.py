from django.conf import settings
from django.utils.translation import gettext_lazy
from rest_framework import serializers

from apps.notice.models import Robot


class NoticeRequestSerializer(serializers.Serializer):
    """
    Notice Base
    """

    usernames = serializers.ListField(
        label=gettext_lazy("Username List"), child=serializers.CharField(label=gettext_lazy("Username"))
    )
    content = serializers.JSONField(label=gettext_lazy("Content"))


class MailContentSerializer(serializers.Serializer):
    """
    Mail Content
    """

    title = serializers.CharField(label=gettext_lazy("Title"))
    content = serializers.CharField(label=gettext_lazy("Content"))


class MailRequestSerialzier(NoticeRequestSerializer):
    """
    Mail
    """

    content = MailContentSerializer(label=gettext_lazy("Content"))


class SmsContentSerializer(serializers.Serializer):
    """
    SMS Content
    """

    tid = serializers.CharField(label=gettext_lazy("Template ID"))
    params = serializers.ListSerializer(label=gettext_lazy("Params"), child=serializers.CharField())


class SmsRequestSerializer(NoticeRequestSerializer):
    """
    SMS
    """

    content = SmsContentSerializer(label=gettext_lazy("Content"))


class RegistryRobotSerializer(serializers.ModelSerializer):
    """
    registry robot
    """

    class Meta:
        model = Robot
        fields = "__all__"


class RobotRequestSerializer(serializers.Serializer):
    """
    Robot
    """

    robots = serializers.ListField(
        label=gettext_lazy("Robot ID"), child=serializers.CharField(label=gettext_lazy("Robot ID"))
    )
    content = serializers.JSONField(label=gettext_lazy("Content"), help_text=settings.NOTICE_ROBOT_CONTENT_HELP)
