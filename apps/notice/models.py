from django.db import models
from django.utils.translation import gettext_lazy

from core.constants import MAX_CHAR_LENGTH, SHORT_CHAR_LENGTH
from core.models import BaseModel, UniqIDField


class NoticeLog(BaseModel):
    """
    Notice Log
    """

    id = UniqIDField(gettext_lazy("ID"))
    receivers = models.JSONField(gettext_lazy("Receivers"))
    content = models.JSONField(gettext_lazy("Content"))
    extra_params = models.JSONField(gettext_lazy("Extra Params"), default=dict, null=True)
    result = models.TextField(gettext_lazy("Result"), blank=True, null=True)
    send_at = models.DateTimeField(gettext_lazy("Send At"), auto_now_add=True)

    class Meta:
        verbose_name = gettext_lazy("Notice Log")
        verbose_name_plural = verbose_name
        ordering = ["-send_at"]


class WecomRobot(BaseModel):
    """
    Wecom Robot
    """

    id = UniqIDField(gettext_lazy("ID"))
    webhook = models.CharField(gettext_lazy("Webhook"), max_length=MAX_CHAR_LENGTH)
    name = models.CharField(gettext_lazy("Name"), max_length=SHORT_CHAR_LENGTH)

    class Meta:
        verbose_name = gettext_lazy("Wecom Robot")
        verbose_name_plural = verbose_name
        ordering = ["id"]
