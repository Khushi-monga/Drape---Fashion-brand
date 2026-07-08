from dataclasses import dataclass
from decimal import Decimal

from products.models import Product


@dataclass
class GuestCartItem:

    product: Product

    quantity: int

    @property
    def unit_price(self):
        return self.product.base_price

    @property
    def subtotal(self):
        return self.product.base_price * self.quantity
    
class GuestCart:

    def __init__(self, request):
        self.request = request

    @property
    def items(self):
        return GuestCartService.get_items(self.request)

    @property
    def subtotal(self):
        return GuestCartService.subtotal(self.request)

    @property
    def total_items(self):
        return GuestCartService.total_items(self.request)


class GuestCartService:

    SESSION_KEY = "cart"

    # ---------- Private Helpers ---------- #

    @classmethod
    def get_or_create_cart(cls, request):
        return GuestCart(request)

    @classmethod
    def _get_cart(cls, request):

        return request.session.setdefault(
            cls.SESSION_KEY,
            {},
        )

    @classmethod
    def _save(cls, request, cart):

        request.session[cls.SESSION_KEY] = cart
        request.session.modified = True

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

        # if quantity > product.stock:
        #     raise ValueError(
        #         "Requested quantity exceeds available stock."
        #     )
        pass

    # ---------- Public API ---------- #

    @classmethod
    def get_cart(cls, request):

        return cls._get_cart(request)

    @classmethod
    def get_cart_item(
        cls,
        request,
        product,
    ):

        cart = cls._get_cart(request)

        quantity = cart.get(
            str(product.id)
        )

        if quantity is None:
            return None

        return GuestCartItem(
            product=product,
            quantity=quantity,
        )

    @classmethod
    def get_items(cls, request):

        cart = cls._get_cart(request)

        if not cart:
            return []

        products = Product.objects.in_bulk(
            map(int, cart.keys())
        )

        items = []

        for product_id, quantity in cart.items():

            product = products.get(
                int(product_id)
            )

            if product:

                items.append(

                    GuestCartItem(
                        product=product,
                        quantity=quantity,
                    )

                )

        return items

    @classmethod
    def add(
        cls,
        request,
        product_id,
        quantity=1,
    ):

        cls._validate_quantity(quantity)

        product = cls._get_product(product_id)

        cls._validate_product(product)

        cart = cls._get_cart(request)

        current = cart.get(
            str(product_id),
            0,
        )

        new_quantity = current + quantity

        cls._validate_stock(
            product,
            new_quantity,
        )

        cart[str(product_id)] = new_quantity

        cls._save(
            request,
            cart,
        )

        guest_cart = cls.get_or_create_cart(request)

        cart_item = cls.get_cart_item(
            request,
            product,
        )

        return guest_cart, cart_item

    @classmethod
    def update(
        cls,
        request,
        product_id,
        quantity,
    ):

        cls._validate_quantity(quantity)

        product = cls._get_product(product_id)

        cls._validate_stock(
            product,
            quantity,
        )

        cart = cls._get_cart(request)

        cart[str(product_id)] = quantity

        cls._save(
            request,
            cart,
        )

        guest_cart = cls.get_or_create_cart(request)

        cart_item = cls.get_cart_item(
            request,
            product,
        )

        return guest_cart, cart_item

    @classmethod
    def remove(
        cls,
        request,
        product_id,
    ):

        cart = cls._get_cart(request)

        cart.pop(
            str(product_id),
            None,
        )

        cls._save(
            request,
            cart,
        )

        return cls.get_or_create_cart(request)

    @classmethod
    def clear(cls, request):

        request.session.pop(
            cls.SESSION_KEY,
            None,
        )

        request.session.modified = True

        return cls.get_or_create_cart(request)

    @classmethod
    def total_items(cls, request):

        return sum(
            cls._get_cart(request).values()
        )

    @classmethod
    def subtotal(cls, request):

        total = Decimal("0.00")

        for item in cls.get_items(request):

            total += item.subtotal

        return total