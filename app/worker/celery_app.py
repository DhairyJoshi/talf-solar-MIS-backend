import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "talf_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.task_routes = {"app.worker.tasks.*": "main-queue"}
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "nightly-yield-sync-placeholder": {
            "task": "app.worker.tasks.sync_nightly_yield",
            "schedule": crontab(hour=2, minute=0),
            "args": (1,),
        },
    },
)