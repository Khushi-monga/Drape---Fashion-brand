from django.db import transaction
from django.db.models import Prefetch

from products.models import Product

from .exceptions import (
    CartItemNotFound,
    InvalidQuantity,
    OutOfStock,
    ProductNotFound,
    ProductUnavailable,
)
from .models import Cart, CartItem


class CartService:

    @staticmethod
    def get_or_create_cart(request):
        """
        Returns the authenticated user's cart with all cart items
        and their associated products prefetched.
        """

        if not request.user.is_authenticated:
            raise NotImplementedError("Guest cart not implemented yet.")

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        return (
            Cart.objects
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=CartItem.objects.select_related("product")
                )
            )
            .get(pk=cart.pk)
        )

    # ------------------------------------------------------------------
    # Private Helper Methods
    # ------------------------------------------------------------------

    @staticmethod
    def _get_product(product_id):
        try:
            return Product.objects.get(pk=product_id)

        except Product.DoesNotExist:
            raise ProductNotFound("Product does not exist.")

    @staticmethod
    def _get_cart_item(cart, product_id):
        try:
            return CartItem.objects.get(
                cart=cart,
                product_id=product_id,
            )

        except CartItem.DoesNotExist:
            raise CartItemNotFound("Item not found in cart.")

    @staticmethod
    def _validate_product(product):
        """
        Adjust these checks according to your Product model.
        """

        if hasattr(product, "is_active") and not product.is_active:
            raise ProductUnavailable(
                "This product is unavailable."
            )

    @staticmethod
    def _validate_quantity(quantity):
        if quantity < 1:
            raise InvalidQuantity(
                "Quantity must be at least 1."
            )

    @staticmethod
    def _validate_stock(product, quantity):
        """
        Skip this check if your Product model doesn't yet have stock.
        """

        if hasattr(product, "stock"):
            if quantity > product.stock:
                raise OutOfStock(
                    f"Only {product.stock} item(s) available."
                )

    # ------------------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def add(request, product_id, quantity=1):

        CartService._validate_quantity(quantity)

        cart = CartService.get_or_create_cart(request)

        product = CartService._get_product(product_id)

        CartService._validate_product(product)
        CartService._validate_stock(product, quantity)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            CartService._validate_stock(product, new_quantity)

            cart_item.quantity = new_quantity
            cart_item.save(update_fields=["quantity", "updated_at"])

        return cart, cart_item

    @staticmethod
    @transaction.atomic
    def update(request, product_id, quantity):

        CartService._validate_quantity(quantity)

        cart = CartService.get_or_create_cart(request)

        cart_item = CartService._get_cart_item(
            cart,
            product_id,
        )

        CartService._validate_stock(
            cart_item.product,
            quantity,
        )

        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity", "updated_at"])

        return cart, cart_item

    @staticmethod
    @transaction.atomic
    def remove(request, product_id):

        cart = CartService.get_or_create_cart(request)

        cart_item = CartService._get_cart_item(
            cart,
            product_id,
        )

        cart_item.delete()

    @staticmethod
    @transaction.atomic
    def clear(request):

        cart = CartService.get_or_create_cart(request)

        cart.items.all().delete()