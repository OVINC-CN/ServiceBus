import abc

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from django.utils.translation import gettext_lazy

from apps.account.constants import UserTypeChoices
from core.constants import MEDIUM_CHAR_LENGTH, SHORT_CHAR_LENGTH
from core.models import ForeignKey, SoftDeletedModel


class User(SoftDeletedModel, AbstractUser):
    """
    User
    """

    user_type = models.CharField(
        gettext_lazy("User Type"),
        choices=UserTypeChoices.choices,
        max_length=SHORT_CHAR_LENGTH,
        default=UserTypeChoices.PERSONAL.value,
    )

    class Meta:
        verbose_name = gettext_lazy("User")
        verbose_name_plural = verbose_name
        ordering = ["username"]


class UserProperty(models.Model):
    """
    User Property
    """

    user = ForeignKey(gettext_lazy("User"), to="account.User", on_delete=models.CASCADE)
    property_key = models.CharField(gettext_lazy("Property Key"), max_length=MEDIUM_CHAR_LENGTH)
    property_val = models.JSONField(gettext_lazy("Property Value"), null=True, default=dict)


class CustomAnonymousUser(AnonymousUser, abc.ABC):
    """
    Anonymous User
    """

    user_type = UserTypeChoices.PLATFORM.value
