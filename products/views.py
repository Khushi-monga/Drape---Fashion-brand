from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import Product
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from products.services.search import ProductSearchService
from .models import Product, Category, Brand
from cart.models import CartItem
from cart.services.services import CartService



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
    

class ProductDetailView(DetailView):

    model = Product

    template_name = "product_detail.html"

    context_object_name = "product"

    slug_field = "slug"

    slug_url_kwarg = "slug"

    queryset = (
        Product.objects
        .select_related(
            "brand",
            "category",
        )
        .filter(
            is_active=True
        )
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        cart_item = CartService.get_cart_item(
            request=self.request,
            product=self.object,
        )

        context["is_in_cart"] = cart_item is not None

        context["cart_quantity"] = (

            cart_item.quantity

            if cart_item

            else 1

        )

        return context