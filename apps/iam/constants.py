from django.utils.translation import gettext_lazy

from core.models import TextChoices


class PermissionStatusChoices(TextChoices):
    DENIED = "denied", gettext_lazy("denied")
    ALLOWED = "allowed", gettext_lazy("allowed")
    DEALING = "dealing", gettext_lazy("dealing")
