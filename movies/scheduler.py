from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from .models import Seat


def release_expired_seats():

    expired_time = timezone.now() - timedelta(minutes=2)

    Seat.objects.filter(
        is_locked=True,
        locked_at__lt=expired_time
    ).update(
        is_locked=False,
        locked_at=None
    )


def start():

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        release_expired_seats,
        'interval',
        minutes=1
    )

    scheduler.start()