import abc
from typing import List

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, AnonymousUser, PermissionsMixin
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext, gettext_lazy

from apps.account.constants import UserTypeChoices
from core.constants import MEDIUM_CHAR_LENGTH, SHORT_CHAR_LENGTH
from core.logger import logger
from core.models import BaseModel, ForeignKey, SoftDeletedManager, SoftDeletedModel


class UserManager(SoftDeletedManager, _UserManager):
    """
    User Manager
    """

    def create_user(self, username, nick_name=None, password=None, **extra_fields):
        if not username:
            raise ValueError(gettext("Username Cannot be Empty"))
        user = self.model(username=username, nick_name=nick_name, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nick_name=None, password=None, **extra_fields):
        extra_fields["is_superuser"] = True
        self.create_user(username, nick_name, password, **extra_fields)


class User(SoftDeletedModel, AbstractBaseUser, PermissionsMixin):
    """
    User
    """

    username = models.CharField(
        gettext_lazy("username"),
        max_length=SHORT_CHAR_LENGTH,
        primary_key=True,
        validators=[AbstractUser.username_validator],
    )
    nick_name = models.CharField(gettext_lazy("Nick Name"), max_length=SHORT_CHAR_LENGTH, blank=True, null=True)
    user_type = models.CharField(
        gettext_lazy("User Type"),
        choices=UserTypeChoices.choices,
        max_length=SHORT_CHAR_LENGTH,
        default=UserTypeChoices.PERSONAL.value,
    )
    date_joined = models.DateTimeField(gettext_lazy("Date Joined"), auto_now_add=True)

    USERNAME_FIELD = "username"
    objects = UserManager()
    _objects = _UserManager()

    class Meta:
        verbose_name = gettext_lazy("User")
        verbose_name_plural = verbose_name
        ordering = ["username"]

    def list_properties(self, key: str = None) -> QuerySet:
        """
        List Properties
        """

        _properties = UserProperty.objects.filter(user=self)
        if key:
            _properties.filter(property_key=key)
        return _properties

    @transaction.atomic()
    def set_properties(self, properties: list[dict]) -> List["UserProperty"]:
        """
        Batch Create or Update Properties
        """

        _properties = []
        for p in properties:
            _property = UserProperty.objects.get_or_create(user=self, property_key=p["property_key"])[0]
            _property.property_val = p["property_val"]
            _property.save()
            _properties.append(_property)
        return _properties

    @transaction.atomic()
    def del_properties(self, property_keys: List[str]) -> None:
        """
        Batch Delete Properties
        """

        _properties = UserProperty.objects.filter(property_key__in=property_keys, user=self)
        logger.info("[UserProperty Deleting] User => %s; Properties => %s", str(self), ",".join(property_keys))
        _properties.delete()


class UserProperty(BaseModel):
    """
    User Property
    """

    user = ForeignKey(gettext_lazy("User"), to="account.User", on_delete=models.CASCADE)
    property_key = models.CharField(gettext_lazy("Property Key"), max_length=MEDIUM_CHAR_LENGTH)
    property_val = models.JSONField(gettext_lazy("Property Value"), null=True, default=dict)

    def __str__(self):
        return self.property_key

    class Meta:
        verbose_name = gettext_lazy("User Property")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
        unique_together = [["user", "property_key"]]


class CustomAnonymousUser(AnonymousUser, abc.ABC):
    """
    Anonymous User
    """

    nick_name = "AnonymousUser"
    user_type = UserTypeChoices.PLATFORM.value
