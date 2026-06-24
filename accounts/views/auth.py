from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.forms import RegistrationForm, LoginForm
from accounts.services.jwt_utils import generate_tokens
from accounts.services.otp_utils import create_or_update_otp, send_otp_email
from accounts.models import EmailVerificationOTP


from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

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

        if not request.session.get(
            "pending_registration"
        ):
            return redirect("register")

        otp_resent = request.session.pop(
            "otp_resent",
            False,
        )

        return render(
            request,
            self.template_name,
            {
                "otp_resent": otp_resent,
            },
        )

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
    

class ResendOTPView(View):

    def post(self, request):

        pending_registration = request.session.get(
            "pending_registration"
        )

        if not pending_registration:
            return redirect("register")

        email = pending_registration["email"]

        otp = create_or_update_otp(email)

        send_otp_email(email, otp)

        request.session["otp_resent"] = True

        return redirect("verify_otp")
    

class LoginView(FormView):
    template_name = "login.html"
    form_class = LoginForm

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



class ForgotPasswordView(View):

    template_name = "forgot_password.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
        )

    def post(self, request):

        email = request.POST.get("email")

        try:
            User.objects.get(email=email)

        except User.DoesNotExist:
            return render(
                request,
                self.template_name,
                {
                    "error":
                        "No account exists with that email."
                },
            )

        otp = create_or_update_otp(email)

        send_otp_email(email, otp)

        request.session[
            "password_reset_email"
        ] = email

        return redirect(
            "password_reset_verify"
        )
    


class PasswordResetOTPView(View):

    template_name = "password_reset_verify.html"

    def get(self, request):

        if not request.session.get(
            "password_reset_email"
        ):
            return redirect(
                "forgot_password"
            )

        return render(
            request,
            self.template_name,
        )

    def post(self, request):

        email = request.session.get(
            "password_reset_email"
        )

        entered_otp = request.POST.get(
            "otp"
        )

        try:
            otp_record = (
                EmailVerificationOTP.objects.get(
                    email=email
                )
            )

        except EmailVerificationOTP.DoesNotExist:
            return render(
                request,
                self.template_name,
                {
                    "error":
                        "OTP not found."
                },
            )

        if (
            otp_record.expires_at
            < timezone.now()
        ):
            otp_record.delete()

            return render(
                request,
                self.template_name,
                {
                    "error":
                        "OTP has expired."
                },
            )

        if otp_record.otp != entered_otp:

            return render(
                request,
                self.template_name,
                {
                    "error":
                        "Invalid OTP."
                },
            )

        request.session[
            "password_reset_verified"
        ] = True

        return redirect(
            "reset_password"
        )
    


class ResetPasswordView(View):

    template_name = "reset_password.html"

    def get(self, request):

        if not request.session.get(
            "password_reset_verified"
        ):
            return redirect(
                "forgot_password"
            )

        return render(
            request,
            self.template_name,
        )

    def post(self, request):

        if not request.session.get(
            "password_reset_verified"
        ):
            return redirect(
                "forgot_password"
            )

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(
                request,
                self.template_name,
                {
                    "error": "Passwords do not match."
                }
            )

        email = request.session.get(
            "password_reset_email"
        )

        user = User.objects.get(
            email=email
        )

        # Prevent reusing current password
        if user.check_password(password1):
            return render(
                request,
                self.template_name,
                {
                    "error": (
                        "Your new password cannot be the same "
                        "as your current password."
                    )
                }
            )

        # Run Django password validators
        try:
            validate_password(
                password1,
                user=user,
            )

        except ValidationError as e:
            return render(
                request,
                self.template_name,
                {
                    "error": " ".join(e.messages)
                }
            )

        user.set_password(password1)
        user.save()

        EmailVerificationOTP.objects.filter(
            email=email
        ).delete()

        request.session.pop(
            "password_reset_email",
            None,
        )

        request.session.pop(
            "password_reset_verified",
            None,
        )

        return redirect("login")