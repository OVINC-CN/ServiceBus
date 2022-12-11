import abc
from typing import List

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, AnonymousUser, PermissionsMixin
from django.contrib.auth.models import UserManager as _UserManager
from django.core.cache import cache
from django.db import models, transaction
from django.db.models import QuerySet
from django.utils.translation import gettext, gettext_lazy

from apps.account.constants import UserCacheKey, UserTypeChoices
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

    def get_cache_user(self, username: str) -> "User":
        """
        get cached user or create cached user
        """

        # get user first
        cache_key = self.model.session_cache_key(username)
        user = cache.get(cache_key)
        if user:
            return user
        # create cache if not exist
        user = self.get(username=username)
        cache.set(cache_key, user, self.model.session_cache_timeout())
        return self.get_cache_user(username)


class User(SoftDeletedModel, AbstractBaseUser, PermissionsMixin):
    """
    User
    """

    username = models.CharField(
        gettext_lazy("username"),
        max_length=SHORT_CHAR_LENGTH,
        primary_key=True,
        validators=[AbstractUser.username_validator],
        error_messages={"unique": gettext_lazy("already in use")},
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

    @classmethod
    def session_cache_key(cls, username) -> str:
        """
        Session Cache Key
        """

        return UserCacheKey.SESSION_USER.format(username=username)

    @classmethod
    def session_cache_timeout(cls) -> int:
        """
        Session Cache Age
        """

        return UserCacheKey.SESSION_USER_TIMEOUT

    def clean_session_cache(self) -> None:
        """
        Cleand Session Cache
        """

        cache.delete(self.session_cache_key(self.username))

    def save(self, *args, **kwargs) -> None:
        """
        Save User
        """

        self.clean_session_cache()
        return super().save()

    def delete(self, *args, **kwargs) -> None:
        """
        Delete User
        """

        self.clean_session_cache()
        return super().delete(*args, **kwargs)


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
        ordering = ["user", "property_key"]
        unique_together = [["user", "property_key"]]


class CustomAnonymousUser(AnonymousUser, abc.ABC):
    """
    Anonymous User
    """

    nick_name = "AnonymousUser"
    user_type = UserTypeChoices.PLATFORM.value
