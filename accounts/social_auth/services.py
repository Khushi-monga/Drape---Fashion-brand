from django.contrib.auth.models import User

from .models import SocialAccount


def get_or_create_google_user(google_data):
    """
    Handles Google login/signup.

    Returns:
        (user, created)

    created:
        True  -> brand new user
        False -> existing user
    """

    google_id = google_data["google_id"]
    email = google_data["email"]
    first_name = google_data["first_name"]
    last_name = google_data["last_name"]

    # --------------------------------------------------
    # 1. Existing Google account already linked
    # --------------------------------------------------

    social_account = SocialAccount.objects.filter(
        provider="google",
        unique_id=google_id,
    ).select_related("user").first()

    if social_account:
        return social_account.user, False

    # --------------------------------------------------
    # 2. Existing User with same email
    # --------------------------------------------------

    user = User.objects.filter(
        email=email
    ).first()

    if user:

        SocialAccount.objects.create(
            user=user,
            provider="google",
            unique_id=google_id,
        )

        return user, False

    # --------------------------------------------------
    # 3. Brand new user
    # --------------------------------------------------

    username = email.split("@")[0]

    original_username = username
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{original_username}{counter}"
        counter += 1

    user = User.objects.create(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    user.set_unusable_password()
    user.save()

    SocialAccount.objects.create(
        user=user,
        provider="google",
        unique_id=google_id,
    )

    return user, True