from django.db.models import QuerySet
from django.contrib.postgres.search import SearchQuery, SearchRank
from products.models import Product
from products.models import Brand, Category
from django.core.cache import cache
from django.db.models import F
from difflib import get_close_matches
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from django.db.models import Value



STOP_WORDS = {
    "for", "the", "a", "an", "of", "in", "on",
    "with", "and", "or", "to", "by", "from"
}

GENDER_KEYWORDS = {
    "men": "M",
    "man": "M",
    "male": "M",
    "mens": "M",
    "man's": "M",

    "women": "W",
    "woman": "W",
    "female": "W",
    "womens": "W",
    "woman's": "W",

    "unisex": "U",
}


class ProductSearchService:

    @classmethod
    def search(cls, query):

        query = query.strip()

        if not query:
            return Product.objects.none()

        parsed = cls.parse_query(query)

        queryset = cls.base_queryset()

        queryset = cls.apply_filters(queryset, parsed)

        full_text_results = cls.full_text_search(queryset, parsed)

        if full_text_results.count() >= 5:
            return cls.rank_results(full_text_results)

        fuzzy_results = cls.fuzzy_search(queryset, parsed)

        return cls.rank_results(fuzzy_results)


    @staticmethod
    def get_brand_lookup():
        brands = cache.get("search_brands")

        if brands is None:
            brands = {
                brand.name.lower(): brand
                for brand in Brand.objects.all()
            }
            cache.set("search_brands", brands, 3600)

        return brands

    @staticmethod
    def get_category_lookup():
        categories = cache.get("search_categories")

        if categories is None:
            categories = {
                category.name.lower(): category
                for category in Category.objects.all()
            }
            cache.set("search_categories", categories, 3600)

        return categories
    
    @staticmethod
    def find_best_match(word, lookup, cutoff=0.8):
        """
        Try exact match first.
        If that fails, try fuzzy matching.
        """

        # Exact match
        if word in lookup:
            return lookup[word]

        # Fuzzy match
        matches = get_close_matches(
            word,
            lookup.keys(),
            n=1,
            cutoff=cutoff
        )

        if matches:
            return lookup[matches[0]]

        return None

    @staticmethod
    def parse_query(query):

        words = query.lower().split()

        parsed = {
            "keywords": [],
            "gender": None,
            "brand": None,
            "category": None,
        }

        brands = ProductSearchService.get_brand_lookup()
        categories = ProductSearchService.get_category_lookup()

        for word in words:

            # Ignore stop words
            if word in STOP_WORDS:
                continue

            # -------------------------
            # Gender (Exact + Fuzzy)
            # -------------------------
            gender = ProductSearchService.find_best_match(
                word,
                GENDER_KEYWORDS,
                cutoff=0.8,
            )

            if gender:
                parsed["gender"] = gender
                continue

            # -------------------------
            # Brand (Exact + Fuzzy)
            # -------------------------
            brand = ProductSearchService.find_best_match(
                word,
                brands,
                cutoff=0.8,
            )

            if brand:
                parsed["brand"] = brand
                continue

            # -------------------------
            # Category (Exact + Fuzzy)
            # -------------------------
            category = ProductSearchService.find_best_match(
                word,
                categories,
                cutoff=0.8,
            )

            if category:
                parsed["category"] = category
                continue

            # -------------------------
            # Remaining search keywords
            # -------------------------
            parsed["keywords"].append(word)

        parsed["keywords"] = " ".join(parsed["keywords"])

        return parsed

    @staticmethod
    def base_queryset():
        return Product.objects.filter(is_active=True)

    @staticmethod
    def apply_filters(queryset, parsed):

        if parsed["gender"]:
            queryset = queryset.filter(gender=parsed["gender"])

        if parsed["brand"]:
            queryset = queryset.filter(brand=parsed["brand"])

        if parsed["category"]:
            queryset = queryset.filter(category=parsed["category"])

        return queryset

    @staticmethod
    def full_text_search(queryset, parsed):

        keywords = parsed["keywords"]

        if not keywords:
            return queryset

        search_query = SearchQuery(
            keywords,
            search_type="websearch",
        )

        return (
            queryset
            .annotate(
                rank=SearchRank(
                    F("search_vector"),
                    search_query,
                )
            )
            .filter(rank__gt=0)
        )

    @staticmethod
    def fuzzy_search(queryset, parsed):

        keywords = parsed["keywords"].split()

        if not keywords:
            return queryset.none()

        similarity_expressions = []

        for keyword in keywords:

            similarity_expressions.extend([
                TrigramSimilarity("name", keyword),
                TrigramSimilarity("search_tags", keyword),
                TrigramSimilarity("description", keyword),
                TrigramSimilarity("brand__name", keyword),
                TrigramSimilarity("category__name", keyword),
            ])

        queryset = queryset.annotate(
            similarity=Greatest(
                *similarity_expressions,
                Value(0.0),
            )
        )

        return (
            queryset
            .filter(similarity__gt=0.3)
            .order_by("-similarity", "name")
        )

    @staticmethod
    def rank_results(queryset):
        return queryset