from django.utils.translation import gettext_lazy

from core.models import TextChoices


class UserTypeChoices(TextChoices):
    """
    User Type Choices
    """

    PERSONAL = "personal", gettext_lazy("Personal")
    PLATFORM = "platform", gettext_lazy("Platform")
