from apps.cel import app
from core.logger import celery_logger


@app.task(bind=True)
def send_notice(self, notice_type: str, **kwargs):
    from apps.notice.utils import NoticeBase

    celery_logger.info(f"[SendNotice] Start {self.request.id}")
    NoticeBase.get_instance(notice_type, **kwargs).send()
    celery_logger.info(f"[SendNotice] End {self.request.id}")
