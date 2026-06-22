import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .google_utils import verify_google_token
from .services import get_or_create_google_user
from accounts.jwt_utils import generate_tokens


@require_POST
def google_auth_view(request):

    try:
        body = json.loads(request.body)

        google_token = body.get("token")

        if not google_token:
            return JsonResponse(
                {"error": "Google token missing"},
                status=400
            )

        # Verify token with Google
        google_data = verify_google_token(
            google_token
        )

        if not google_data["email_verified"]:
            return JsonResponse(
                {"error": "Google email is not verified"},
                status=400
            )

        # Login / Signup logic
        user, created = get_or_create_google_user(
            google_data
        )

        # Generate JWT tokens
        access_token, refresh_token = generate_tokens(
            user
        )

        response = JsonResponse({
            "success": True,
            "created": created,
        })

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,      # True in production
            samesite="Lax",
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,      # True in production
            samesite="Lax",
        )

        return response

    except ValueError:
        return JsonResponse(
            {"error": "Invalid Google token"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )