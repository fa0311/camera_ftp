from __future__ import annotations

from celery import Celery

from app.settings import settings

celery_app = Celery(
    "photoftp",
    broker=settings.broker_url,
    backend=settings.backend_url,
    include=["app.queue.tasks"],
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
