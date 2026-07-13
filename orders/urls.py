from django.urls import path

from .views import (
    CheckoutView,
    CreateOrderView,
    ChangeAddressView,
    SelectCheckoutAddressView
)


urlpatterns = [
    path("checkout/",CheckoutView.as_view(),name="checkout"),
    path("create/", CreateOrderView.as_view(), name="create-order"),
    path("change-address/",ChangeAddressView.as_view(),name="change-address"),
    path("select-address/<int:pk>/",SelectCheckoutAddressView.as_view(),name="select-checkout-address",),
]