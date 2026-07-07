from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .services import CartService


class CartView(LoginRequiredMixin, View):

    def get(self, request):

        cart = CartService.get_or_create_cart(request)

        return render(
            request,
            "cart.html",
            {
                "cart": cart,
            },
        )


class AddToCartView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        quantity = int(request.POST.get("quantity", 1))

        CartService.add(
            request=request,
            product_id=product_id,
            quantity=quantity,
        )

        messages.success(request, "Product added to cart.")

        return redirect(
            "product_detail",
            slug=CartService._get_product(product_id).slug,
        )


class UpdateCartView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        quantity = int(request.POST.get("quantity", 1))

        CartService.update(
            request=request,
            product_id=product_id,
            quantity=quantity,
        )

        messages.success(request, "Cart updated.")

        return redirect("cart:cart")


class UpdateCartAjaxView(LoginRequiredMixin, View):

    def post(self, request):

        product_id = request.POST.get("product_id")
        quantity = request.POST.get("quantity")

        if not product_id or not quantity:

            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid request.",
                },
                status=400,
            )

        try:

            cart, cart_item = CartService.update(
                request=request,
                product_id=int(product_id),
                quantity=int(quantity),
            )

            return JsonResponse(
                {
                    "success": True,
                    "quantity": cart_item.quantity,
                    "item_subtotal": str(cart_item.subtotal),
                    "cart_subtotal": str(cart.subtotal),
                    "cart_items": cart.total_items,
                }
            )

        except Exception as e:

            return JsonResponse(
                {
                    "success": False,
                    "message": str(e),
                },
                status=400,
            )


class RemoveCartItemView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        CartService.remove(
            request=request,
            product_id=product_id,
        )

        messages.success(request, "Product removed from cart.")

        return redirect("cart:cart")


class ClearCartView(LoginRequiredMixin, View):

    def post(self, request):

        CartService.clear(request)

        messages.success(request, "Cart cleared.")

        return redirect("cart:cart")