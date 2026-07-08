from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from accounts.models import Address


class AddAddressView(LoginRequiredMixin, CreateView):

    model = Address

    fields = [
        "full_name",
        "phone",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
    ]

    template_name = "add_address.html"


    def form_valid(self, form):

        form.instance.user = self.request.user

        return super().form_valid(form)


    def get_success_url(self):

        return "/orders/checkout/"