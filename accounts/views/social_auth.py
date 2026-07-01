from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
import secrets

import requests

from django.http import HttpResponseBadRequest

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth.exceptions import GoogleAuthError

from accounts.services.social_auth import (
    get_or_create_google_user,
)
from accounts.services.jwt_utils import generate_tokens
from accounts.services.auth_service import login_user_response


class GoogleLoginView(View):

    def get(self, request):

        # state = secrets.token_urlsafe(32)

        # request.session["google_oauth_state"] = state

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
            #"state": state,
        }

        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urlencode(params)
        )

        #print("STATE GENERATED:", state)
        print("AUTH URL:", auth_url)

        return redirect(auth_url)



class GoogleCallbackView(View):
    def get(self, request):

        # state = request.GET.get("state")
        # expected_state = request.session.pop(
        #     "google_oauth_state",
        #     None,
        # )
        # if not state or state != expected_state:
        #     return HttpResponseBadRequest(
        #         "Invalid OAuth state."
        #     )

        code = request.GET.get("code")

        if not code:
            return HttpResponseBadRequest(
                "Authorization code missing."
            )

        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10,
        )

        if token_response.status_code != 200:
            return HttpResponseBadRequest(
                token_response.text
            )

        token_data = token_response.json()

        google_id_token = token_data.get("id_token")

        if not google_id_token:
            return HttpResponseBadRequest(
                "Missing Google ID token."
            )

        try:
            payload = id_token.verify_oauth2_token(
                google_id_token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )

            if payload.get("iss") not in (
                "accounts.google.com",
                "https://accounts.google.com",
            ):
                return HttpResponseBadRequest(
                    "Invalid token issuer."
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponseBadRequest(str(e))

        email = payload.get("email")

        if not email:
            return HttpResponseBadRequest(
                "Email not provided by Google."
            )

        if not payload.get("email_verified"):
            return HttpResponseBadRequest(
                "Google email not verified."
            )

        provider_uid = payload["sub"]

        first_name = payload.get(
            "given_name",
            "",
        )

        last_name = payload.get(
            "family_name",
            "",
        )

        user = get_or_create_google_user(
            provider_uid=provider_uid,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        return login_user_response(user)