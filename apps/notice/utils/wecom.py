from typing import List, Union

import requests

from apps.notice.models import WecomRobot
from apps.notice.utils.base import NoticeBase
from core.logger import logger


class RobotHandler(NoticeBase):
    """
    Wecom Robot
    """

    property_key = None

    def __init__(self, robots: List[str], content: Union[dict, str], **kwargs) -> None:
        super().__init__(robots, content, **kwargs)

    def _send(self) -> list:
        result = []
        web = requests.session()
        for robot in self.receivers:
            resp = web.post(robot, json=self.content)
            result.append(resp.json())
        return result

    def _load_receivers(self, robot_ids: List[str]) -> List[str]:
        """
        wecom robot id
        """

        logger.info("[%s LoadReceivers] Robots => %s", self.__class__.__name__, robot_ids)
        robots = WecomRobot.objects.filter(id__in=robot_ids)
        logger.info(
            "[%s LoadReceivers] Receivers => %s",
            self.__class__.__name__,
            [f"{r.id}:{r.webhook}" for r in robots],
        )
        return [r.webhook for r in robots]
