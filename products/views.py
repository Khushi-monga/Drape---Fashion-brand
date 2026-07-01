from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import Product
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity


class ProductSearchView(ListView):
    model = Product
    template_name = "search_results.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()

        if not query:
            return Product.objects.none()

        search_query = SearchQuery(query, search_type="websearch")

        qs = (
            Product.objects.filter(is_active=True)
            .annotate(
                rank=SearchRank(F("search_vector"), search_query),
                similarity=TrigramSimilarity("name", query),
            )
            .annotate(
                score=F("rank") + F("similarity")
            )
            .filter(score__gt=0)
            .order_by("-score")
        )

        return qs

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

    queryset = Product.objects.select_related(
        "brand",
        "category",
    ).filter(
        is_active=True
    )