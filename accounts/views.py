from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate
from .jwt_utils import generate_tokens
from .otp_utils import create_or_update_otp, send_otp_email
from django.contrib.auth.models import User
from django.utils import timezone
from .models import EmailVerificationOTP
from django.conf import settings


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():

            request.session["pending_registration"] = {
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "password": form.cleaned_data["password1"],
            }

            email = form.cleaned_data["email"]

            otp = create_or_update_otp(email)

            send_otp_email(email, otp)

            return redirect("verify_otp")

    else:
        form = RegistrationForm()

    return render(
        request,
        "register.html",
        {
            "form": form,
            "google_client_id": settings.GOOGLE_CLIENT_ID,
        }
    )




def verify_otp_view(request):

    pending_registration = request.session.get(
        "pending_registration"
    )

    if not pending_registration:
        return redirect("register")

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        email = pending_registration["email"]

        try:
            otp_record = EmailVerificationOTP.objects.get(
                email=email
            )

        except EmailVerificationOTP.DoesNotExist:

            return render(
                request,
                "verify_otp.html",
                {
                    "error": "OTP not found. Please register again."
                }
            )

        if otp_record.expires_at < timezone.now():

            otp_record.delete()

            return render(
                request,
                "verify_otp.html",
                {
                    "error": "OTP has expired. Please register again."
                }
            )

        if otp_record.otp != entered_otp:

            return render(
                request,
                "verify_otp.html",
                {
                    "error": "Invalid OTP."
                }
            )

        User.objects.create_user(
            username=pending_registration["username"],
            email=pending_registration["email"],
            password=pending_registration["password"],
            first_name=pending_registration["first_name"],
            last_name=pending_registration["last_name"],
        )
        request.session.flush()
        otp_record.delete()

        return redirect("login")

    return render(
        request,
        "verify_otp.html"
    )

from django.http import JsonResponse

def session_debug(request):
    return JsonResponse(dict(request.session))


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                access_token, refresh_token = generate_tokens(user)

                response = redirect("home")

                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    samesite="Lax",
                    secure=True,  # True in production
                )

                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    samesite="Lax",
                    secure=True,  # True in production
                    max_age=60 * 15,
                )

                return response

            form.add_error(
                None,
                "Invalid username or password."
            )

    else:
        form = LoginForm()

    return render(
        request,
        "login.html",
        {
            "form": form,
            "google_client_id": settings.GOOGLE_CLIENT_ID,
        }
    )

def logout_view(request):
    response = redirect("home")

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")

    return response