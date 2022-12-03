from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy
from rest_framework import serializers

from apps.account.models import User, UserProperty

USER_MODEL: User = get_user_model()


class UserInfoSerializer(serializers.ModelSerializer):
    """
    User Info
    """

    class Meta:
        model = USER_MODEL
        fields = ["username", "nick_name", "last_login", "user_type"]


class UserPropertyRequestSerializer(serializers.Serializer):
    """
    User Property Request
    """

    key = serializers.IntegerField(label=gettext_lazy("Property Key"), required=False)


class UserPropertySerializer(serializers.ModelSerializer):
    """
    User Property
    """

    class Meta:
        model = UserProperty
        fields = "__all__"


class UserPropertyCreateSerializer(serializers.ModelSerializer):
    """
    Create User Property
    """

    class Meta:
        model = UserProperty
        fields = ["property_key", "property_val"]


class UserPropertyDeleteSerializer(serializers.Serializer):
    """
    Delete User Property
    """

    property_keys = serializers.ListField(
        label=gettext_lazy("Property Keys"), child=serializers.CharField(label=gettext_lazy("Property Key"))
    )


class SignInSerializer(serializers.Serializer):
    """
    Sign in
    """

    username = serializers.CharField(label=gettext_lazy("Username"))
    password = serializers.CharField(label=gettext_lazy("password"))


class VerifyUserTokenRequestSerializer(serializers.Serializer):
    """
    Verify User Token
    """

    token = serializers.CharField(label=gettext_lazy("Auth Token"))


class UserRegistrySerializer(serializers.ModelSerializer):
    """
    User Registry
    """

    class Meta:
        model = USER_MODEL
        fields = "__all__"
