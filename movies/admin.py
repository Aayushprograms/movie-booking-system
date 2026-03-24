from django.contrib import admin
from .models import Movie, Genre, Language, Booking, Seat


# -----------------------------
# Genre Admin
# -----------------------------
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


# -----------------------------
# Language Admin
# -----------------------------
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]


# -----------------------------
# Movie Admin
# -----------------------------
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "language", "rating", "release_date"]
    list_filter = ["language", "genres"]
    search_fields = ["title"]
    ordering = ["title"]


# -----------------------------
# Seat Admin (Task 5)
# -----------------------------
@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):

    list_display = [
        "seat_number",
        "movie",
        "show_time",
        "is_locked",
        "locked_at",
    ]

    list_filter = [
        "movie",
        "show_time",
        "is_locked",
    ]

    search_fields = [
        "seat_number",
        "movie__title",
    ]

    ordering = ["movie", "show_time", "seat_number"]


# -----------------------------
# Booking Admin
# -----------------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = [
        "user_email",
        "movie",
        "show_time",
        "seat_numbers",
        "payment_id",
        "status",
        "created_at",
    ]

    search_fields = [
        "user_email",
        "payment_id",
    ]

    list_filter = [
        "movie",
        "show_time",
        "status",
    ]

    ordering = ["-created_at"]