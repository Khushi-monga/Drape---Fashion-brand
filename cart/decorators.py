# cart/decorators.py

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .exceptions import CartError


def handle_cart_errors(success_message=None, redirect_to="cart:cart"):
    """
    Handles CartService exceptions and optionally displays a success message.
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):

            try:
                response = view_func(self, request, *args, **kwargs)

                if success_message:
                    messages.success(request, success_message)

                return response

            except CartError as e:
                messages.error(request, str(e))
                return redirect(redirect_to)

            except Exception:
                messages.error(
                    request,
                    "Something went wrong. Please try again."
                )
                return redirect(redirect_to)

        return wrapper

    return decorator