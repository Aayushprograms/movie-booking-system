
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect("movies/")),
    path("admin/", admin.site.urls),
    path("movies/", include("movies.urls")),
]