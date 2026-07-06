# cart/exceptions.py

class CartError(Exception):
    """Base exception for all cart-related errors."""
    pass


class ProductNotFound(CartError):
    pass


class ProductUnavailable(CartError):
    pass


class OutOfStock(CartError):
    pass


class InvalidQuantity(CartError):
    pass


class CartItemNotFound(CartError):
    pass