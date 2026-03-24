from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_booking_email(self, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        subject = "🎬 Movie Booking Confirmation"
        message = f"""
Hello,

Your booking is confirmed!

Movie: {booking.movie.title}
Show Time: {booking.show_time}
Seats: {booking.seat_numbers}
Payment ID: {booking.payment_id}

Enjoy your movie 🍿
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [booking.user_email],
            fail_silently=False,
        )

    except Booking.DoesNotExist:
        print("Booking not found")