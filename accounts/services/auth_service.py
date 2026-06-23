from django.shortcuts import redirect
from accounts.services.jwt_utils import generate_tokens

def login_user_response(user):
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