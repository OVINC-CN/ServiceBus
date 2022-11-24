from apps.cel import app
from core.logger import celery_logger


@app.task(bind=True)
def celery_debug(self):
    celery_logger.info(f"[CeleryDebug] Start {self.request.id}")
    celery_logger.info(f"[CeleryDebug] End {self.request.id}")
