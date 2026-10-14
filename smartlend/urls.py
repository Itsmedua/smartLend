"""Top-level URL routes: which address goes to which part of the project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Gives us /accounts/login/ and /accounts/logout/ for free
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
]
