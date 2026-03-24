from django.urls import path
from . import views
from .views import reserve_seat
from .views import admin_dashboard

urlpatterns = [

    path("", views.movie_list, name="movie_list"),

    path("api/", views.movie_filter_api, name="movie_filter_api"),

    path("<int:pk>/", views.movie_detail, name="movie_detail"),
    path("seats/reserve/<int:seat_id>/", reserve_seat, name="reserve_seat"),
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),

    path(
        "payment/create/<int:booking_id>/",
        views.create_booking_payment,
        name="create_payment"
    ),

    path(
        "payment/verify/",
        views.verify_payment,
        name="verify_payment"
    ),

    path(
        "payment/webhook/",
        views.razorpay_webhook,
        name="razorpay_webhook"
    ),

    # ADD THIS
    path(
        "seats/reserve/<int:seat_id>/",
        views.reserve_seat,
        name="reserve_seat"
    ),
]