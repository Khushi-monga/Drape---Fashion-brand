from django.contrib.postgres.search import SearchQuery

from products.models import Product


class ProductSearchService:

    @staticmethod
    def search(query: str):

        if not query:
            return Product.objects.none()

        search_query = SearchQuery(query)

        return Product.objects.filter(search_vector=search_query)