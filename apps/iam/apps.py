from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.iam"
    verbose_name = gettext_lazy("User Permission")
