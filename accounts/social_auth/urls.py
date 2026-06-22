from django.urls import path
from .views import google_auth_view

urlpatterns = [
    path(
        "google/", google_auth_view, name="google_auth"),
]
