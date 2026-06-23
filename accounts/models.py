from django.db import models
from django.contrib.auth.models import User


class EmailVerificationOTP(models.Model):

    email = models.EmailField(unique=True,db_index=True)

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.email} - {self.otp}"
    



class SocialAccount(models.Model):

    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )

    provider = models.CharField(
        max_length=50,
        choices=Provider.choices,
    )

    provider_uid = models.CharField(
        max_length=255,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_uid"],
                name="unique_social_account"
            )
        ]

        indexes = [
            models.Index(
                fields=["provider", "provider_uid"],
                name="social_account_lookup_idx",
            )
        ]

    def __str__(self):
        return f"{self.provider}:{self.provider_uid}"