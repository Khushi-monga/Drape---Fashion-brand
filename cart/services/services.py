from .guest_cart import GuestCartService
from .user_cart import UserCartService


class CartService:

    # ---------- Internal ---------- #

    @staticmethod
    def _get_service(request):

        if request.user.is_authenticated:
            return UserCartService

        return GuestCartService

    # ---------- Cart API ---------- #

    @classmethod
    def get_or_create_cart(cls, request):

        if request.user.is_authenticated:
            return UserCartService.get_or_create_cart(request)

        return GuestCartService.get_or_create_cart(request)

    @classmethod
    def get_cart_item(
        cls,
        request,
        product,
    ):

        return cls._get_service(request).get_cart_item(
            request,
            product,
        )

    @classmethod
    def get_items(cls, request):

        return cls._get_service(request).get_items(request)

    @classmethod
    def add(
        cls,
        request,
        product_id,
        quantity=1,
    ):

        return cls._get_service(request).add(
            request,
            product_id,
            quantity,
        )

    @classmethod
    def update(
        cls,
        request,
        product_id,
        quantity,
    ):

        return cls._get_service(request).update(
            request,
            product_id,
            quantity,
        )

    @classmethod
    def remove(
        cls,
        request,
        product_id,
    ):

        return cls._get_service(request).remove(
            request,
            product_id,
        )

    @classmethod
    def clear(cls, request):

        return cls._get_service(request).clear(request)

    @classmethod
    def subtotal(cls, request):

        return cls._get_service(request).subtotal(request)

    @classmethod
    def total_items(cls, request):

        return cls._get_service(request).total_items(request)

    # ---------- Guest Cart Merge ---------- #

    @staticmethod
    def has_guest_cart(request):

        return bool(
            GuestCartService.get_cart(request)
        )

    @staticmethod
    def merge_guest_cart(request, user):

        if not user.is_authenticated:
            return 

        if not CartService.has_guest_cart(request):
            return

        guest_cart = GuestCartService.get_cart(request)

        for product_id, quantity in guest_cart.items():

            UserCartService.add(
                request=request,
                user=user,
                product_id=int(product_id),
                quantity=quantity,
            )

        GuestCartService.clear(request)