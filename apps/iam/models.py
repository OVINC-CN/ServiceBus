from django.db import models
from django.utils.translation import gettext_lazy

from apps.iam.constants import PermissionStatusChoices
from core.constants import SHORT_CHAR_LENGTH
from core.models import BaseModel, ForeignKey, UniqIDField


class Action(BaseModel):
    """
    Action
    """

    id = UniqIDField(gettext_lazy("ID"))
    application = ForeignKey(gettext_lazy("Application"), to="application.Application", on_delete=models.CASCADE)
    action_id = models.CharField(gettext_lazy("Action ID"), max_length=SHORT_CHAR_LENGTH)
    action_name = models.CharField(gettext_lazy("Action Name"), max_length=SHORT_CHAR_LENGTH)
    resource_id = models.CharField(gettext_lazy("Resource ID"), max_length=SHORT_CHAR_LENGTH, null=True, blank=True)
    resource_name = models.CharField(gettext_lazy("Resource Name"), max_length=SHORT_CHAR_LENGTH, null=True, blank=True)
    description = models.TextField(gettext_lazy("Description"), null=True, blank=True)

    class Meta:
        verbose_name = gettext_lazy("Action")
        verbose_name_plural = verbose_name
        ordering = ["id"]
        unique_together = [["application", "action_id"]]


class Instance(BaseModel):
    """
    Instance
    """

    id = UniqIDField(gettext_lazy("ID"))
    application = ForeignKey(gettext_lazy("Application"), to="application.Application", on_delete=models.CASCADE)
    resource_id = models.CharField(gettext_lazy("Resource ID"), max_length=SHORT_CHAR_LENGTH, null=True, blank=True)
    instance_id = models.CharField(gettext_lazy("Instance ID"), max_length=SHORT_CHAR_LENGTH)
    instance_name = models.CharField(gettext_lazy("Instance Name"), max_length=SHORT_CHAR_LENGTH)

    class Meta:
        verbose_name = gettext_lazy("Resource")
        verbose_name_plural = verbose_name
        ordering = ["id"]
        unique_together = [["application", "resource_id", "instance_id"]]


class UserPermissionBase(BaseModel):
    """
    User Permission Base
    """

    id = UniqIDField(gettext_lazy("ID"))
    user = ForeignKey(gettext_lazy("User"), to="account.User", on_delete=models.CASCADE)
    action = ForeignKey(gettext_lazy("Action"), to="iam.Action", on_delete=models.CASCADE)
    instances = models.JSONField(gettext_lazy("Instances"), default=list, null=True)
    all_instances = models.BooleanField(gettext_lazy("All Instances"), default=False)
    status = models.CharField(
        gettext_lazy("Status"),
        max_length=SHORT_CHAR_LENGTH,
        choices=PermissionStatusChoices.choices,
        default=PermissionStatusChoices.DEALING,
        db_index=True,
    )
    update_at = models.DateTimeField(gettext_lazy("Update At"), auto_now=True)

    class Meta:
        abstract = True


class UserPermission(UserPermissionBase):
    """
    User Permission
    """

    class Meta:
        verbose_name = gettext_lazy("User Permission")
        verbose_name_plural = verbose_name
        ordering = ["action", "-update_at"]
        index_together = [["user", "action", "status"]]
        unique_together = [["user", "action"]]


class UserPermissionSnapshot(UserPermissionBase):
    """
    User Permission Snapshot
    """

    class Meta:
        verbose_name = gettext_lazy("User Permission Snapshot")
        verbose_name_plural = verbose_name
        ordering = ["action", "-update_at"]
        index_together = [["user", "action", "status"]]
        unique_together = [["user", "action"]]
