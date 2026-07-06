from .models import Cart


def cart(request):
    if not request.user.is_authenticated:
        return {
            "cart": None,
            "cart_item_count": 0,
            "cart_total": 0,
        }

    try:
        cart = request.user.cart

    except Cart.DoesNotExist:
        return {
            "cart": None,
            "cart_item_count": 0,
            "cart_total": 0,
        }

    return {
        "cart": cart,
        "cart_item_count": cart.total_items,
        "cart_total": cart.subtotal,
    }