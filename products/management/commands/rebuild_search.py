from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector

from products.models import Product


class Command(BaseCommand):
    help = "Rebuild search_vector for all products"

    def handle(self, *args, **kwargs):

        products = Product.objects.all()

        for product in products:
            Product.objects.filter(id=product.id).update(
                search_vector=(
                    SearchVector("name", weight="A") +
                    SearchVector("description", weight="B") +
                    SearchVector("search_tags", weight="C")
                )
            )

        self.stdout.write(self.style.SUCCESS("Search vectors rebuilt"))