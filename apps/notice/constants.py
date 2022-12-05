from django.utils.translation import gettext_lazy

from core.models import TextChoices


class NoticeWayChoices(TextChoices):
    MSG = "msg", gettext_lazy("msg")
    MAIL = "mail", gettext_lazy("mail")
    Robot = "robot", gettext_lazy("robot")
