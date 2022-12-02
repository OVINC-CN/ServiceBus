from typing import List, Union

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend

from apps.account.constants import UserPropertyChoices
from apps.notice.utils.base import NoticeBase


class MailHandler(NoticeBase):
    """
    Send Mail
    """

    def __init__(self, usernames: List[str], content: Union[dict, str], **kwargs) -> None:
        super().__init__(usernames=usernames, content=content, **kwargs)
        self.host = settings.NOTICE_MAIL_HOST
        self.port = settings.NOTICE_MAIL_PORT
        self.username = settings.NOTICE_MAIL_USERNAME
        self.password = settings.NOTICE_MAIL_PASSWORD

    @property
    def property_key(self) -> str:
        return UserPropertyChoices.MAIL_ADDRESS.value

    def _send(self) -> None:
        connection = EmailBackend(
            host=self.host, port=self.port, username=self.username, password=self.password, use_ssl=True
        )
        return send_mail(
            subject=self.content["title"],
            message=self.content["content"],
            from_email=self.username,
            recipient_list=self.receivers,
            connection=connection,
        )
