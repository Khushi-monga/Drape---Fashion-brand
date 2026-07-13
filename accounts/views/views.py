from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.views import View
from accounts.models import Address
from django.shortcuts import redirect, get_object_or_404


class AddAddressView(LoginRequiredMixin, CreateView):

    model = Address

    fields = [
        "title",
        "full_name",
        "phone",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
        "is_default",
    ]

    template_name = "add_address.html"


    def form_valid(self, form):

        form.instance.user = self.request.user

        return super().form_valid(form)


    def get_success_url(self):

        return "/orders/checkout/"
    

class SetDefaultAddressView(LoginRequiredMixin, View):

    def post(self, request, pk):

        address = get_object_or_404(
            Address,
            id=pk,
            user=request.user
        )


        address.is_default = True
        address.save()
        
        return redirect(
            "checkout"
        )