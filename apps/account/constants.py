from django.utils.translation import gettext_lazy

from core.models import TextChoices


class UserTypeChoices(TextChoices):
    """
    User Type Choices
    """

    PERSONAL = "personal", gettext_lazy("Personal")
    PLATFORM = "platform", gettext_lazy("Platform")


class UserPropertyChoices(TextChoices):
    """
    User Property
    """

    PHONE_NUMBER = "phone_number", gettext_lazy("Phone Number")
    MAIL_ADDRESS = "mail_address", gettext_lazy("Mail Address")
