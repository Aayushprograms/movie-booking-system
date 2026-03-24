from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models.functions import ExtractHour

import json
import hmac
import hashlib
import uuid

from .models import Movie, Genre, Language, Booking, PaymentWebhookEvent, Seat
from .utils import get_youtube_embed_url


# -----------------------------------
# EXPIRE OLD BOOKINGS
# -----------------------------------
def expire_old_bookings():
    expired_time = timezone.now() - timedelta(minutes=60)

    Booking.objects.filter(
        status="PENDING",
        created_at__lt=expired_time
    ).update(status="EXPIRED")


# -----------------------------------
# MOVIE LIST
# -----------------------------------
def movie_list(request):

    selected_language = request.GET.get("language")
    selected_genres = request.GET.getlist("genres")

    sort_by = request.GET.get("sort", "title")
    page_number = request.GET.get("page", 1)

    queryset = Movie.objects.all()

    # -----------------------------
    # FILTERS
    # -----------------------------
    if selected_language:
        queryset = queryset.filter(language__name=selected_language)

    if selected_genres:
        queryset = queryset.filter(genres__name__in=selected_genres)

    queryset = queryset.distinct()

    # -----------------------------
    # SORTING
    # -----------------------------
    sort_map = {
        "rating": "-rating",
        "release_date": "-release_date",
        "title": "title"
    }

    queryset = queryset.order_by(sort_map.get(sort_by, "title"))

    # Optimization
    queryset = queryset.select_related("language").prefetch_related("genres")

    # -----------------------------
    # PAGINATION
    # -----------------------------
    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(page_number)

    # -----------------------------
    # GENRE COUNTS (FIXED PART)
    # -----------------------------
    count_base_queryset = Movie.objects.all()

    if selected_language:
        count_base_queryset = count_base_queryset.filter(
            language__name=selected_language
        )

    genre_counts = (
        count_base_queryset
        .values("genres__name")
        .annotate(count=Count("id"))
    )

    genre_count_dict = {
        item["genres__name"]: item["count"]
        for item in genre_counts
        if item["genres__name"]
    }

    # -----------------------------
    # CONTEXT
    # -----------------------------
    context = {
        "page_obj": page_obj,
        "selected_language": selected_language,
        "selected_genres": selected_genres,
        "sort_by": sort_by,
        "genre_count_dict": genre_count_dict,
        "all_genres": Genre.objects.all(),
        "all_languages": Language.objects.all(),
    }

    return render(request, "movies/movie_list.html", context)

# -----------------------------------
# MOVIE DETAIL
# -----------------------------------
def movie_detail(request, pk):

    movie = get_object_or_404(Movie, pk=pk)

    embed_url = get_youtube_embed_url(movie.trailer_url)

    return render(request, "movies/movie_detail.html", {
        "movie": movie,
        "embed_url": embed_url,
    })
def movie_filter_api(request):

    movies = Movie.objects.all()

    language = request.GET.get("language")
    genres = request.GET.getlist("genres")

    if language:
        movies = movies.filter(language__name=language)

    if genres:
        movies = movies.filter(genres__name__in=genres)

    movies = movies.distinct()

    data = list(
        movies.values(
            "id",
            "title",
            "rating",
            "release_date",
            "language__name"
        )
    )

    return JsonResponse({"movies": data})


# -----------------------------------
# CREATE PAYMENT ORDER
# -----------------------------------
def create_booking_payment(request, booking_id):

    expire_old_bookings()

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status != "PENDING":
        return JsonResponse({"error": "Invalid booking state"}, status=400)

    fake_order_id = "order_" + str(uuid.uuid4())

    booking.razorpay_order_id = fake_order_id
    booking.save(update_fields=["razorpay_order_id"])

    return JsonResponse({
        "order_id": fake_order_id,
        "amount": booking.amount,
        "key": "mock_key"
    })


# -----------------------------------
# VERIFY PAYMENT
# -----------------------------------
@csrf_exempt
@transaction.atomic
def verify_payment(request):

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")

    booking = Booking.objects.select_for_update().filter(
        razorpay_order_id=razorpay_order_id
    ).first()

    if not booking:
        return JsonResponse({"status": "booking_not_found"})

    if booking.status == "PAID":
        return JsonResponse({"status": "already_processed"})

    booking.payment_id = razorpay_payment_id
    booking.status = "PAID"
    booking.save()

    return JsonResponse({"status": "payment_success"})


# -----------------------------------
# WEBHOOK
# -----------------------------------
@csrf_exempt
def razorpay_webhook(request):

    payload = request.body
    signature = request.headers.get("X-Razorpay-Signature")

    expected_signature = hmac.new(
        bytes(settings.RAZORPAY_WEBHOOK_SECRET, "utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        return JsonResponse({"error": "Invalid signature"}, status=400)

    event = json.loads(payload)
    event_id = event["payload"]["payment"]["entity"]["id"]

    if PaymentWebhookEvent.objects.filter(event_id=event_id).exists():
        return JsonResponse({"status": "duplicate_event"})

    PaymentWebhookEvent.objects.create(
        event_id=event_id,
        payload=event
    )

    return JsonResponse({"status": "processed"})


# -----------------------------------
# RELEASE EXPIRED SEATS
# -----------------------------------
def release_expired_seats():
    expired_time = timezone.now() - timedelta(minutes=2)

    Seat.objects.filter(
        is_locked=True,
        locked_at__lt=expired_time
    ).update(
        is_locked=False,
        locked_at=None
    )


# -----------------------------------
# RESERVE SEAT (Concurrency Safe)
# -----------------------------------
@transaction.atomic
def reserve_seat(request, seat_id):

    release_expired_seats()

    seat = Seat.objects.select_for_update().get(id=seat_id)

    if seat.is_locked:
        return JsonResponse({"error": "Seat already locked"}, status=400)

    seat.is_locked = True
    seat.locked_at = timezone.now()
    seat.save()

    return JsonResponse({
        "status": "seat_locked",
        "seat": seat.seat_number
    })


# -----------------------------------
# ADMIN DASHBOARD (OPTIMIZED)
# -----------------------------------
@staff_member_required
def admin_dashboard(request):

    data = cache.get("dashboard_data")

    if not data:

        now = timezone.now()

        # Revenue
        daily_revenue = Booking.objects.filter(
            status="PAID",
            created_at__date=now.date()
        ).aggregate(total=Sum("amount"))["total"] or 0

        weekly_revenue = Booking.objects.filter(
            status="PAID",
            created_at__gte=now - timedelta(days=7)
        ).aggregate(total=Sum("amount"))["total"] or 0

        monthly_revenue = Booking.objects.filter(
            status="PAID",
            created_at__gte=now - timedelta(days=30)
        ).aggregate(total=Sum("amount"))["total"] or 0

        # Popular Movies
        popular_movies = (
            Booking.objects
            .values("movie__title")
            .annotate(total=Count("id"))
            .order_by("-total")[:5]
        )

        # Peak Hours
        peak_hours = (
            Booking.objects
            .annotate(hour=ExtractHour("created_at"))
            .values("hour")
            .annotate(total=Count("id"))
            .order_by("hour")
        )

        # Busiest Movies (Seat Occupancy)
        busiest_movies = (
            Booking.objects
            .values("movie__title")
            .annotate(total=Count("seat_numbers"))
            .order_by("-total")[:5]
        )

        # Cancellation Rate
        total = Booking.objects.count()
        cancelled = Booking.objects.filter(status="CANCELLED").count()

        cancellation_rate = (cancelled / total * 100) if total else 0

        data = {
            "daily_revenue": daily_revenue,
            "weekly_revenue": weekly_revenue,
            "monthly_revenue": monthly_revenue,
            "popular_movies": list(popular_movies),
            "peak_hours": list(peak_hours),
            "busiest_movies": list(busiest_movies),
            "cancellation_rate": round(cancellation_rate, 2),
        }

        cache.set("dashboard_data", data, timeout=60)

    return render(request, "movies/admin_dashboard.html", data)