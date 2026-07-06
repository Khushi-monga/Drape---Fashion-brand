from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from django.http import HttpResponse

from .decorators import handle_cart_errors
from .services import CartService


class CartView(LoginRequiredMixin, View):

    def get(self, request):
        return HttpResponse("Cart View Works")

    template_name = "cart.html"

    def get(self, request):
        cart = CartService.get_or_create_cart(request)

        return render(
            request,
            self.template_name,
            {
                "cart": cart,
            },
        )


class AddToCartView(LoginRequiredMixin, View):

    @handle_cart_errors()
    def post(self, request, product_id):
        CartService.add(
            request=request,
            product_id=product_id,
        )

        messages.success(request, "Product added to cart.")

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "cart:cart",
            )
        )


class UpdateCartView(LoginRequiredMixin, View):

    @staticmethod
    def _get_quantity(request):
        try:
            quantity = int(request.POST.get("quantity", 1))
            return max(1, quantity)
        except (TypeError, ValueError):
            return 1

    @handle_cart_errors()
    def post(self, request, product_id):
        CartService.update(
            request=request,
            product_id=product_id,
            quantity=self._get_quantity(request),
        )

        messages.success(request, "Cart updated.")

        return redirect("cart:cart")


class RemoveCartItemView(LoginRequiredMixin, View):

    @handle_cart_errors()
    def post(self, request, product_id):
        CartService.remove(
            request=request,
            product_id=product_id,
        )

        messages.success(request, "Item removed from cart.")

        return redirect("cart:cart")


class ClearCartView(LoginRequiredMixin, View):

    @handle_cart_errors()
    def post(self, request):
        CartService.clear(request)

        messages.success(request, "Cart cleared.")

        return redirect("cart:cart")