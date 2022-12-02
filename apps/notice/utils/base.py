import abc
import traceback
from typing import List, Union

from django.utils.module_loading import import_string
from django.utils.translation import gettext

from apps.account.models import UserProperty
from apps.cel.tasks import send_notice
from apps.notice.constants import NoticeWayChoices
from apps.notice.models import NoticeLog
from core.logger import logger


class NoticeBase:
    """
    Notice Base
    """

    @classmethod
    def send_notice(cls, notice_type: str, is_async: bool = True, **kwargs) -> None:
        if is_async:
            send_notice.delay(notice_type, **kwargs)
            return None
        send_notice(notice_type, **kwargs)

    @classmethod
    def get_instance(cls, notice_type: str, **kwargs) -> "NoticeBase":
        instance_map = {_value: f"apps.notice.utils.{_value.capitalize()}Handler" for _value in NoticeWayChoices.values}
        try:
            notice_type_class = import_string(instance_map[notice_type])
            return notice_type_class(**kwargs)
        except KeyError:
            raise KeyError(gettext("Notice Type not Exists => %s") % notice_type)

    def __init__(self, usernames: List[str], content: Union[dict, str], **kwargs) -> None:
        self.receivers = self._load_receivers(usernames)
        self.content = self._build_content(content)
        self.kwargs = kwargs

    @property
    @abc.abstractmethod
    def property_key(self) -> str:
        raise NotImplementedError

    def send(self) -> None:
        """
        send notice
        """

        logger.info("[%s SendNotice] Content => %s", self.__class__.__name__, self.content)
        try:
            result = self._send()
            logger.info("[%s SendNoticeSuccess] Result => %s", self.__class__.__name__, result)
        except Exception as err:
            msg = traceback.format_exc()
            logger.error("[%s SendNoticeFailed] Err => %s; Detail => %s", self.__class__.__name__, err, msg)
            result = {"err": str(err)}
        NoticeLog.objects.create(
            receivers=self.receivers, content=self.content, extra_params=self.kwargs, result=str(result)
        )
        return result

    @abc.abstractmethod
    def _send(self) -> None:
        """
        send notice
        """

        raise NotImplementedError

    def _load_receivers(self, usernames: List[str]) -> List[str]:
        """
        trans username to receiver
        """

        logger.info("[%s LoadReceivers] Usernames => %s", self.__class__.__name__, usernames)
        # load property
        user_properties = UserProperty.objects.filter(user_id__in=usernames, property_key=self.property_key)
        logger.info(
            "[%s LoadReceivers] Receivers => %s",
            self.__class__.__name__,
            [f"{p.user_id}:{p.property_val}" for p in user_properties],
        )
        # return
        receivers = list(user_properties.values_list("property_val", flat=True))
        return receivers

    def _build_content(self, content: Union[dict, str]) -> any:
        """
        build content for notice
        """

        return content
