from apps.cel.tasks.debug import celery_debug
from apps.cel.tasks.notice import send_notice

__all__ = [
    "celery_debug",
    "send_notice",
]
