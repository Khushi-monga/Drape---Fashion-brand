from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    ClearCartView,
    RemoveCartItemView,
    UpdateCartView,
)

app_name = "cart"

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("add/<int:product_id>/", AddToCartView.as_view(), name="add"),
    path("update/<int:product_id>/", UpdateCartView.as_view(), name="update"),
    path("remove/<int:product_id>/", RemoveCartItemView.as_view(), name="remove"),
    path("clear/", ClearCartView.as_view(), name="clear"),
]