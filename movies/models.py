from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import uuid


# -----------------------------
# YouTube URL Validator
# -----------------------------
def validate_youtube_url(value):
    if not value:
        return

    parsed = urlparse(value)

    allowed_domains = {
        "www.youtube.com",
        "youtube.com",
        "youtu.be",
    }

    if parsed.netloc not in allowed_domains:
        raise ValidationError("Only YouTube URLs are allowed.")


# -----------------------------
# Genre Model
# -----------------------------
class Genre(models.Model):

    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


# -----------------------------
# Language Model
# -----------------------------
class Language(models.Model):

    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


# -----------------------------
# Movie Model (UPDATED ✅)
# -----------------------------
class Movie(models.Model):

    title = models.CharField(max_length=200, db_index=True)

    rating = models.FloatField(db_index=True)

    release_date = models.DateField(db_index=True)

    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name="movies",
        db_index=True
    )

    genres = models.ManyToManyField(Genre, related_name="movies")

    trailer_url = models.URLField(
        blank=True,
        null=True,
        validators=[validate_youtube_url]
    )

    # ✅ NEW FIELD (IMPORTANT)
    poster_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["language", "rating"]),
            models.Index(fields=["language", "release_date"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return self.title


# -----------------------------
# Seat Model (Task 5)
# -----------------------------
class Seat(models.Model):

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    show_time = models.DateTimeField()

    seat_number = models.CharField(max_length=10)

    is_locked = models.BooleanField(default=False)

    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["movie", "show_time", "seat_number"]

    def __str__(self):
        return f"{self.movie.title} - {self.seat_number}"


# -----------------------------
# Booking Model
# -----------------------------
class Booking(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("EXPIRED", "Expired"),
    ]

    user_email = models.EmailField(db_index=True)

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    show_time = models.DateTimeField(db_index=True)

    seat_numbers = models.CharField(max_length=100)

    amount = models.IntegerField(default=0)

    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        unique=True
    )

    payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        unique=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_email", "created_at"]),
            models.Index(fields=["movie", "show_time"]),
        ]

    def __str__(self):
        return f"{self.user_email} - {self.movie.title}"


# -----------------------------
# Webhook Event Model
# -----------------------------
class PaymentWebhookEvent(models.Model):

    event_id = models.CharField(max_length=200, unique=True)

    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)