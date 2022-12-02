from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class NoticeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notice"
    verbose_name = gettext_lazy("Notice")
