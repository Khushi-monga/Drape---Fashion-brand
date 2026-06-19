from django.urls import path, include

from .views import register, login_view, logout_view, verify_otp_view

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path('social_auth/', include('apps.social_auth.urls'), name="social_auth"), 
]