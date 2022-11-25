from django.db import models
from django.db.models import ForeignKey as _ForeignKey
from django.db.models import IntegerChoices as _IntegerChoices
from django.db.models import QuerySet
from django.db.models import TextChoices as _TextChoices
from django.utils.translation import gettext_lazy


class IntegerChoices(_IntegerChoices):
    """
    Int Choices
    """

    @property
    def value(self) -> int:
        """
        Get choice value
        """

        return self._value_


class TextChoices(_TextChoices):
    """
    Text Choices
    """

    @property
    def value(self) -> str:
        """
        Get choice value
        """

        return self._value_


class ForeignKey(_ForeignKey):
    """
    ForeignKey
    """

    def __init__(
        self,
        verbose_name: str,
        to: str,
        on_delete: callable,
        related_name: str = None,
        related_query_name: str = None,
        db_constraint: str = False,
        **kwargs
    ):
        super().__init__(
            to=to,
            on_delete=on_delete,
            related_name=related_name,
            related_query_name=related_query_name,
            db_constraint=db_constraint,
            verbose_name=verbose_name,
            **kwargs,
        )


class BaseModel(models.Model):
    """
    Base Model
    """

    objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.pk

    @classmethod
    def get_queryset(cls) -> QuerySet:
        return cls.objects.all()

    def get_name(self) -> str:
        return str(self)


class SoftDeletedManager(models.Manager):
    """
    Soft Delete Model Manager
    """

    def get(self, *args, **kwargs) -> "SoftDeletedModel":
        kwargs = self._add_soft_delete_param(kwargs)
        return super().get(*args, **kwargs)

    def filter(self, *args, **kwargs) -> QuerySet:
        kwargs = self._add_soft_delete_param(kwargs)
        return super().filter(*args, **kwargs)

    def all(self) -> QuerySet:
        return self.filter()

    def _add_soft_delete_param(self, kwargs) -> dict:
        return {**kwargs, "is_deleted": False}


class SoftDeletedModel(BaseModel):
    """
    Soft Delete Model
    """

    is_deleted = models.BooleanField(gettext_lazy("Soft Delete"), default=False, db_index=True)

    objects = SoftDeletedManager()
    _objects = models.Manager()

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls) -> QuerySet:
        return cls.objects.filter(is_deleted=False)

    def delete(self, *args, **kwargs) -> None:
        self.is_deleted = True
        self.save()