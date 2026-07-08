# from django.urls import path, include

# from .views import register, login_view, logout_view, verify_otp_view

# urlpatterns = [
#     path("register/", register, name="register"),
#     path("login/", login_view, name="login"),
#     path("logout/", logout_view, name="logout"),
#     path("verify-otp/", verify_otp_view, name="verify_otp"),
#     #path('social_auth/', include('apps.social_auth.urls'), name="social_auth"), 
# ]


from django.urls import path
from accounts.views.auth import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    LogoutView,
    ResendOTPView,
    ForgotPasswordView,
    PasswordResetOTPView,
    ResetPasswordView
)
from accounts.views.social_auth import(
    GoogleLoginView,
    GoogleCallbackView
)

from accounts.views.views import AddAddressView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("resend_otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google_callback"),
    path("forgot-password/",ForgotPasswordView.as_view(),name="forgot_password",),
    path("password-reset-verify/",PasswordResetOTPView.as_view(),name="password_reset_verify",),
    path("reset-password/",ResetPasswordView.as_view(),name="reset_password",),
    path("add-address/",AddAddressView.as_view(),name="add-address"),
]