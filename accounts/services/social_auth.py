from django.contrib.auth.models import User
from django.db import transaction

from accounts.models import SocialAccount

import re


def generate_unique_username(email: str) -> str:
    base = email.split("@")[0].lower()

    base = re.sub(r"[^a-z0-9_]", "_", base)

    username = base
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base}_{counter}"
        counter += 1

    return username


@transaction.atomic
def get_or_create_google_user(
    *,
    provider_uid: str,
    email: str,
    first_name: str = "",
    last_name: str = "",
):
    """
    Login flow:

    1. Find existing Google account link.
    2. If not found, find user by email.
    3. If found, link Google account.
    4. If not found, create user and link account.
    """

    social_account = (
        SocialAccount.objects
        .select_related("user")
        .filter(
            provider=SocialAccount.Provider.GOOGLE,
            provider_uid=provider_uid,
        )
        .first()
    )

    if social_account:
        return social_account.user

    user = User.objects.filter(email=email).first()

    if user:
        SocialAccount.objects.create(
            user=user,
            provider=SocialAccount.Provider.GOOGLE,
            provider_uid=provider_uid,
        )

        return user

    username = generate_unique_username(email)

    user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    user.set_unusable_password()
    user.save(update_fields=["password"])

    SocialAccount.objects.create(
        user=user,
        provider=SocialAccount.Provider.GOOGLE,
        provider_uid=provider_uid,
    )

    return user