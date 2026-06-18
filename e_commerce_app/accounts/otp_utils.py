import random

from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import EmailVerificationOTP


def generate_otp():
    """
    Generates a 6-digit OTP as a string.
    Example: '483921'
    """
    return f"{random.randint(100000, 999999)}"


def create_or_update_otp(email):
    """
    Creates a new OTP or replaces the existing one
    for the given email.

    Returns the generated OTP.
    """

    otp = generate_otp()

    expires_at = timezone.now() + timedelta(minutes=10)

    EmailVerificationOTP.objects.update_or_create(
        email=email,
        defaults={
            "otp": otp,
            "expires_at": expires_at,
        }
    )

    return otp


def send_otp_email(email, otp):
    """
    Sends the OTP to the user's email.
    """

    subject = "Email Verification"

    message = f"""
Your verification code is:

{otp}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )