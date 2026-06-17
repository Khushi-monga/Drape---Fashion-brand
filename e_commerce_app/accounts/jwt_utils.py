import jwt

from datetime import datetime, timedelta, timezone

from django.conf import settings


def generate_tokens(user):
    now = datetime.now(timezone.utc)

    access_payload = {
        "user_id": user.id,
        "token_type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES),
    }

    refresh_payload = {
        "user_id": user.id,
        "token_type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
    }

    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return access_token, refresh_token


def verify_token(token, expected_type):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("token_type") != expected_type:
            return None

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None