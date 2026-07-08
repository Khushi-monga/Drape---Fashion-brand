from django.contrib import admin
from .models import EmailVerificationOTP
from .models import Address


admin.site.register(EmailVerificationOTP)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "city",
        "is_default",
    )

    list_filter = (
        "is_default",
    )