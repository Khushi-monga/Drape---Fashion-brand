from django.views.generic import ListView
from django.db.models import Q

from .models import Product


class ProductSearchView(ListView):

    model = Product

    template_name = "search_results.html"

    context_object_name = "products"

    paginate_by = 12

    def get_queryset(self):

        query = self.request.GET.get("q", "").strip()

        if not query:
            return Product.objects.none()

        products = Product.objects.filter(
            is_active=True
        )

        for word in query.split():

            products = products.filter(
                Q(name__icontains=word) |
                Q(description__icontains=word) |
                Q(brand__name__icontains=word) |
                Q(category__name__icontains=word)
            )

        return products.distinct()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["query"] = self.request.GET.get("q", "")

        return context
    

from django.views.generic import DetailView

from .models import Product


class ProductDetailView(DetailView):

    model = Product

    template_name = "products/product_detail.html"

    context_object_name = "product"

    slug_field = "slug"

    slug_url_kwarg = "slug"

    queryset = Product.objects.select_related(
        "brand",
        "category",
    ).filter(
        is_active=True
    )