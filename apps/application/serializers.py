from typing import List

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext, gettext_lazy
from rest_framework import serializers

from apps.account.models import User
from apps.application.constants import APP_CODE_REGEXP
from apps.application.models import Application, ApplicationManager
from core.constants import SHORT_CHAR_LENGTH

USER_MODEL: User = get_user_model()


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Application Info
    """

    class Meta:
        model = Application
        fields = ["app_name", "app_code"]


class ApplicationManagerSerializer(serializers.ModelSerializer):
    """
    Application Manager
    """

    class Meta:
        model = USER_MODEL
        fields = ["username", "nick_name"]


class ApplicationListSerializer(serializers.ModelSerializer):
    """
    Application List
    """

    managers = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ["app_name", "app_code", "managers"]

    def get_managers(self, instance: Application) -> List[dict]:
        return ApplicationManagerSerializer(instance=self.context.get(instance.app_code, []), many=True).data


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    create application
    """

    app_code = serializers.RegexField(
        label=gettext_lazy("App Code"),
        regex=APP_CODE_REGEXP,
        max_length=SHORT_CHAR_LENGTH,
        error_messages={"invalid": gettext_lazy("only support digit, characters, -, _")},
    )
    app_secret = serializers.CharField(label=gettext_lazy("App Secret"))
    managers = serializers.ListField(
        label=gettext_lazy("Managers"), child=serializers.CharField(label=gettext_lazy("Username"))
    )

    class Meta:
        model = Application
        fields = ["app_name", "app_code", "app_secret", "managers"]

    def validate_managers(self, managers: List[str]) -> QuerySet:
        managers = USER_MODEL.objects.filter(username__in=managers)
        if not managers:
            raise serializers.ValidationError(gettext("managers cannot be null"))
        return managers


class ApplicationUpdateRequestSerializer(ApplicationCreateSerializer):
    """
    update application
    """

    class Meta:
        model = Application
        fields = ["app_name", "managers"]

    @transaction.atomic()
    def update(self, instance: Application, validated_data: dict) -> Application:
        """
        update
        """

        # update app_name
        if validated_data.get("app_name"):
            instance.app_name = validated_data["app_name"]

        # update managers
        if validated_data.get("managers"):
            ApplicationManager.objects.filter(application=instance).delete()
            app_managers = [
                ApplicationManager(application=instance, manager=manager) for manager in validated_data["managers"]
            ]
            ApplicationManager.objects.bulk_create(app_managers)

        return instance


class ApplicationUpdateResponseSerializer(serializers.ModelSerializer):
    """
    update application Response
    """

    managers = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ["app_name", "app_code", "managers"]

    def get_managers(self, instance: Application) -> List[dict]:
        managers = ApplicationManager.objects.filter(application=instance).values("manager")
        users = USER_MODEL.objects.filter(username__in=managers)
        return ApplicationManagerSerializer(instance=users, many=True).data
