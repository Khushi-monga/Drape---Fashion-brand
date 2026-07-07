from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import Product
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from products.services.search import ProductSearchService
from .models import Product, Category, Brand
from cart.models import CartItem



class ProductSearchView(ListView):

    model = Product

    template_name = "search_results.html"

    context_object_name = "products"

    paginate_by = 12

    def get_queryset(self):

        query = self.request.GET.get("q", "").strip()

        if not query:
            return Product.objects.none()

        return ProductSearchService.search(query)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["query"] = self.request.GET.get("q", "")

        return context
    



from django.views.generic import DetailView

from cart.models import CartItem
from .models import Product


class ProductDetailView(DetailView):

    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    queryset = Product.objects.select_related(
        "brand",
        "category",
    ).filter(
        is_active=True
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart_item = None

        if self.request.user.is_authenticated:
            cart_item = (
                CartItem.objects.select_related("cart")
                .filter(
                    cart__user=self.request.user,
                    product=self.object,
                )
                .first()
            )

        context["is_in_cart"] = cart_item is not None
        context["cart_quantity"] = cart_item.quantity if cart_item else 1

        return context