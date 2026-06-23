from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from .forms import RegistrationForm, LoginForm
from .services.jwt_utils import generate_tokens
from .services.otp_utils import create_or_update_otp, send_otp_email
from .models import EmailVerificationOTP


import json
from google.oauth2 import id_token
from google.auth.transport import requests

from accounts.services.social_auth import get_or_create_google_user
from accounts.services.auth_service import login_user_response
from django.conf import settings

class RegisterView(FormView):
    template_name = "register.html"
    form_class = RegistrationForm

    def form_valid(self, form):

        self.request.session["pending_registration"] = {
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

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})
    



class VerifyOTPView(View):

    template_name = "verify_otp.html"

    def get(self, request):
        if not request.session.get("pending_registration"):
            return redirect("register")

        return render(request, self.template_name)

    def post(self, request):

        pending_registration = request.session.get("pending_registration")

        if not pending_registration:
            return redirect("register")

        entered_otp = request.POST.get("otp")
        email = pending_registration["email"]

        try:
            otp_record = EmailVerificationOTP.objects.get(email=email)
        except EmailVerificationOTP.DoesNotExist:
            return render(request, self.template_name, {
                "error": "OTP not found. Please register again."
            })

        if otp_record.expires_at < timezone.now():
            otp_record.delete()
            return render(request, self.template_name, {
                "error": "OTP has expired. Please register again."
            })

        if otp_record.otp != entered_otp:
            return render(request, self.template_name, {
                "error": "Invalid OTP."
            })

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
    

class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["GOOGLE_CLIENT_ID"] = settings.GOOGLE_CLIENT_ID
        return context

    def form_valid(self, form):

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(
            self.request,
            username=username,
            password=password
        )

        if user is None:
            form.add_error(None, "Invalid username or password.")
            return self.form_invalid(form)

        access_token, refresh_token = generate_tokens(user)

        response = redirect("home")

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="Lax",
            secure=True,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="Lax",
            secure=True,
            max_age=60 * 15,
        )

        return response
    



class LogoutView(View):

    def get(self, request):
        response = redirect("home")

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        response.delete_cookie("sessionid")
        response.delete_cookie("csrftoken")

        return response
    



class SessionDebugView(View):

    def get(self, request):
        return JsonResponse(dict(request.session))
    


class GoogleAuthView(View):

    def post(self, request):

        try:
            body = json.loads(request.body)
            token = body.get("token")

            # 1. verify google token
            id_info = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            if id_info["aud"] != settings.GOOGLE_CLIENT_ID:
                return JsonResponse({"error": "Invalid token"}, status=400)

            if not id_info.get("email_verified"):
                return JsonResponse({"error": "Email not verified"}, status=400)

            # 2. get or create user
            user = get_or_create_google_user(id_info)

            # 3. login (JWT)
            return login_user_response(user)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)