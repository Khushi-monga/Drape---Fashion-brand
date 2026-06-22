from django.db import models
from django.contrib.auth.models import User


class SocialAccount(models.Model):

    PROVIDER_CHOICES = [
        ("google", "Google"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="social_accounts"
    )

    provider = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES
    )

    unique_id = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "provider",
            "unique_id"
        )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.provider}"
        )