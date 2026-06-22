from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings


def verify_google_token(token):
    """
    Verifies the Google ID token and returns
    the user's Google profile information.

    Returns:
        {
            "google_id": str,
            "email": str,
            "first_name": str,
            "last_name": str,
            "email_verified": bool
        }

    Raises:
        ValueError if the token is invalid.
    """

    payload = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID,
    )

    return {
        "google_id": payload.get("sub"),
        "email": payload.get("email"),
        "first_name": payload.get("given_name", ""),
        "last_name": payload.get("family_name", ""),
        "email_verified": payload.get("email_verified", False),
    }