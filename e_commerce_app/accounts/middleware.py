from django.contrib.auth.models import AnonymousUser, User
from django.utils.deprecation import MiddlewareMixin

from .jwt_utils import generate_tokens, verify_token


class JWTAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        request._new_access_token = None
        request._new_refresh_token = None

        request.user = AnonymousUser()

        # ----------------------------------------
        # Case 1: Valid access token
        # ----------------------------------------

        if access_token:
            access_payload = verify_token(
                access_token,
                expected_type="access"
            )

            if access_payload:
                user = User.objects.filter(
                    id=access_payload["user_id"]
                ).first()

                if user:
                    request.user = user
                    return

        # ----------------------------------------
        # Case 2: Access expired, refresh valid
        # ----------------------------------------

        if refresh_token:
            refresh_payload = verify_token(
                refresh_token,
                expected_type="refresh"
            )

            if refresh_payload:
                user = User.objects.filter(
                    id=refresh_payload["user_id"]
                ).first()

                if user:
                    request.user = user

                    new_access_token, new_refresh_token = generate_tokens(
                        user
                    )

                    request._new_access_token = new_access_token
                    request._new_refresh_token = new_refresh_token

                    return

        # ----------------------------------------
        # Case 3: Both invalid
        # ----------------------------------------

        request.user = AnonymousUser()

    def process_response(self, request, response):

        new_access_token = getattr(
            request,
            "_new_access_token",
            None
        )

        new_refresh_token = getattr(
            request,
            "_new_refresh_token",
            None
        )

        if new_access_token and new_refresh_token:

            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                samesite="Lax",
                secure=False,  # True in production HTTPS
            )

            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                samesite="Lax",
                secure=False,  # True in production HTTPS
            )

        return response