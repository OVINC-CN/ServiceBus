from typing import List, Union

from django.conf import settings
from tencentcloud.common import credential
from tencentcloud.sms.v20210111 import models, sms_client

from apps.account.constants import UserPropertyChoices
from apps.notice.utils.base import NoticeBase


class MsgHandler(NoticeBase):
    """
    Send SMS
    """

    def __init__(self, usernames: List[str], content: Union[dict, str], **kwargs):
        super().__init__(usernames, content, **kwargs)
        self._cred = credential.Credential(settings.NOTICE_MSG_TCLOUD_ID, settings.NOTICE_MSG_TCLOUD_KEY)
        self._client = sms_client.SmsClient(self._cred, settings.NOTICE_MSG_TCLUD_REGION)

    @property
    def property_key(self):
        return UserPropertyChoices.PHONE_NUMBER.value

    def _send(self) -> None:
        req = models.SendSmsRequest()
        req.SmsSdkAppId = settings.NOTICE_MSG_TCLOUD_APP
        req.SignName = settings.NOTICE_MSG_TCLOUD_SIGN
        req.TemplateId = self.content["tid"]
        req.TemplateParamSet = self.content["params"]
        req.PhoneNumberSet = self.receivers
        resp = self._client.SendSms(req)
        return resp.to_json_string(indent=2)
