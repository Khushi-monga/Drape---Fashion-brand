from django.db import models


class EmailVerificationOTP(models.Model):

    email = models.EmailField(unique=True,db_index=True)

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.email} - {self.otp}"