from django.db import transaction
from django.db.models import Prefetch

from cart.models import Cart, CartItem
from products.models import Product


class UserCart:

    def __init__(self, cart):
        self._cart = cart

    @property
    def items(self):
        return list(self._cart.items.all())

    @property
    def subtotal(self):
        return self._cart.subtotal

    @property
    def total_items(self):
        return self._cart.total_items


class UserCartService:

    # ---------- Private Helpers ---------- #

    @staticmethod
    def _validate_quantity(quantity):

        if quantity < 1:
            raise ValueError(
                "Quantity must be at least 1."
            )

    @staticmethod
    def _get_product(product_id):

        return Product.objects.get(
            pk=product_id,
            is_active=True,
        )

    @staticmethod
    def _validate_product(product):

        if not product.is_active:
            raise ValueError(
                "Product is unavailable."
            )

    @staticmethod
    def _validate_stock(product, quantity):
        pass

    @staticmethod
    def _get_or_create_db_cart(request, user=None):

        user = user or request.user

        cart, _ = Cart.objects.get_or_create(
            user=user,
        )

        return (
            Cart.objects
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=CartItem.objects.select_related(
                        "product"
                    )
                )
            )
            .get(pk=cart.pk)
        )

    @staticmethod
    def _get_cart_item(cart, product_id):

        return CartItem.objects.select_related(
            "product"
        ).get(
            cart=cart,
            product_id=product_id,
        )

    # ---------- Public API ---------- #

    @classmethod
    def get_or_create_cart(
        cls,
        request,
        user=None,
    ):

        return UserCart(
            cls._get_or_create_db_cart(
                request,
                user=user,
            )
        )

    @classmethod
    def get_cart_item(
        cls,
        request,
        product,
        user=None,
    ):

        cart = cls._get_or_create_db_cart(
            request,
            user=user,
        )

        return (
            CartItem.objects
            .select_related("product")
            .filter(
                cart=cart,
                product=product,
            )
            .first()
        )

    @classmethod
    def get_items(
        cls,
        request,
        user=None,
    ):

        cart = cls._get_or_create_db_cart(
            request,
            user=user,
        )

        return cart.items.all()

    @classmethod
    @transaction.atomic
    def add(
        cls,
        request,
        product_id,
        quantity=1,
        user=None,
    ):

        cls._validate_quantity(quantity)

        cart = cls._get_or_create_db_cart(
            request,
            user=user,
        )

        product = cls._get_product(product_id)

        cls._validate_product(product)

        cls._validate_stock(
            product,
            quantity,
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": quantity,
            },
        )

        if not created:

            new_quantity = (
                cart_item.quantity
                + quantity
            )

            cls._validate_stock(
                product,
                new_quantity,
            )

            cart_item.quantity = new_quantity

            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

        cart.refresh_from_db()

        return UserCart(cart), cart_item

    @classmethod
    @transaction.atomic
    def update(
        cls,
        request,
        product_id,
        quantity,
        user=None,
    ):

        cls._validate_quantity(quantity)

        cart = cls._get_or_create_db_cart(
            request,
            user=user,
        )

        cart_item = cls._get_cart_item(
            cart,
            product_id,
        )

        cls._validate_stock(
            cart_item.product,
            quantity,
        )

        cart_item.quantity = quantity

        cart_item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        cart.refresh_from_db()

        return UserCart(cart), cart_item

    @classmethod
    @transaction.atomic
    def remove(
        cls,
        request,
        product_id,
        user=None,
    ):

        cart = cls._get_or_create_db_cart(
            request,
            user=user,
        )

        cart_item = cls._get_cart_item(
            cart,
            product_id,
        )

        cart_item.delete()

        cart.refresh_from_db()

        return UserCart(cart)

    @classmethod
    @transaction.atomic
    def clear(
        cls,
        request,
        user=None,
    ):

        cart = cls._get_or_create_db_cart(
            request,
            user=user,
        )

        cart.items.all().delete()

        cart.refresh_from_db()

        return UserCart(cart)

    @classmethod
    def total_items(
        cls,
        request,
        user=None,
    ):

        return cls.get_or_create_cart(
            request,
            user=user,
        ).total_items

    @classmethod
    def subtotal(
        cls,
        request,
        user=None,
    ):

        return cls.get_or_create_cart(
            request,
            user=user,
        ).subtotal