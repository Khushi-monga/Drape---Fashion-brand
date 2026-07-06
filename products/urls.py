from django.urls import path, include

from .views import (
    ProductDetailView,
    ProductSearchView
)

urlpatterns = [
    path("search/", ProductSearchView.as_view(),name="product_search"),
    path("<slug:slug>/", ProductDetailView.as_view(),name="product_detail"),
]
