from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View

from cart.services.services import CartService
from accounts.models import Address

from .models import Order, OrderItem



class CheckoutView(LoginRequiredMixin, TemplateView):

    template_name = "checkout.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        items = CartService.get_items(
            self.request
        )

        addresses = self.request.user.addresses.all()

        selected_address = None

        selected_id = self.request.session.get(
            "checkout_address_id"
        )

        if selected_id:

            selected_address = addresses.filter(
                id=selected_id
            ).first()

        if not selected_address:

            selected_address = addresses.filter(
                is_default=True
            ).first()

        context["selected_address"] = selected_address
        context["items"] = items
        context["subtotal"] = CartService.subtotal(
            self.request
        )
        return context
    

class ChangeAddressView(LoginRequiredMixin, TemplateView):

    template_name = "select_address.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        context["addresses"] = (
            self.request.user.addresses.all()
        )


        return context
    

from django.views import View


class SelectCheckoutAddressView(LoginRequiredMixin, View):

    def post(self, request, pk):

        address = get_object_or_404(
            Address,
            pk=pk,
            user=request.user,
        )

        request.session["checkout_address_id"] = address.id

        return redirect("checkout")




class CreateOrderView(LoginRequiredMixin, View):
    pass
    # @transaction.atomic
    # def post(self, request):

    #     address_id = request.POST.get(
    #         "address_id"
    #     )


    #     address = get_object_or_404(
    #         Address,
    #         id=address_id,
    #         user=request.user
    #     )


    #     items = CartService.get_items(
    #         request
    #     )


    #     if not items:
    #         return redirect(
    #             "cart-view"
    #         )


    #     subtotal = CartService.subtotal(
    #         request
    #     )


    #     order = Order.objects.create(

    #         user=request.user,

    #         full_name=address.full_name,

    #         phone=address.phone,

    #         address_line_1=address.address_line_1,

    #         address_line_2=address.address_line_2,

    #         city=address.city,

    #         state=address.state,

    #         postal_code=address.postal_code,

    #         country=address.country,

    #         subtotal=subtotal,

    #         shipping_cost=0,

    #         total_amount=subtotal,

    #     )


    #     order_items = []


    #     for item in items:

    #         item_subtotal = (
    #             item.product.base_price
    #             *
    #             item.quantity
    #         )


    #         order_items.append(

    #             OrderItem(

    #                 order=order,

    #                 product=item.product,

    #                 product_name=item.product.name,

    #                 price=item.product.base_price,

    #                 quantity=item.quantity,

    #                 subtotal=item_subtotal,

    #             )

    #         )


    #     OrderItem.objects.bulk_create(
    #         order_items
    #     )


    #     CartService.clear(
    #         request
    #     )


    #     return redirect(
    #         "order-success",
    #         order_id=order.id
    #     )