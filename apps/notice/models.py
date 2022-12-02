from django.db import models
from django.utils.translation import gettext_lazy

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
