from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
import random

from products.models import Category, Brand, Product


class Command(BaseCommand):

    help = "Seed products database"

    def handle(self, *args, **kwargs):

        categories = [
            "Clothing",
            "Footwear",
            "Accessories",
        ]

        brands = [
            "Nike",
            "Adidas",
            "Puma",
            "Reebok",
            "Levis",
            "H&M",
            "Zara",
            "Woodland",
            "Allen Solly",
            "Van Heusen",
            "US Polo",
            "Tommy Hilfiger",
            "Jack & Jones",
            "Roadster",
            "Wrogn",
        ]

        clothing_products = [
            "Classic T-Shirt",
            "Oversized T-Shirt",
            "Slim Fit Shirt",
            "Formal Shirt",
            "Casual Shirt",
            "Denim Jacket",
            "Hoodie",
            "Sweatshirt",
            "Cargo Pants",
            "Slim Fit Jeans",
            "Track Pants",
            "Joggers",
        ]

        footwear_products = [
            "Running Shoes",
            "Sneakers",
            "Training Shoes",
            "Casual Shoes",
            "Leather Boots",
            "Sports Shoes",
            "Slip On Shoes",
            "Canvas Shoes",
        ]

        accessory_products = [
            "Leather Wallet",
            "Backpack",
            "Cap",
            "Belt",
            "Sunglasses",
            "Travel Bag",
            "Laptop Bag",
            "Sports Cap",
        ]

        category_objects = {}

        for category_name in categories:

            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    "slug": slugify(category_name),
                }
            )

            category_objects[category_name] = category

        brand_objects = []

        for brand_name in brands:

            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={
                    "slug": slugify(brand_name),
                }
            )

            brand_objects.append(brand)

        for i in range(100):

            category_name = random.choice(categories)

            if category_name == "Clothing":
                base_name = random.choice(clothing_products)

            elif category_name == "Footwear":
                base_name = random.choice(footwear_products)

            else:
                base_name = random.choice(accessory_products)

            name = f"{base_name} {i}"

            Product.objects.create(
                category=category_objects[category_name],
                brand=random.choice(brand_objects),
                name=name,
                slug=slugify(name),
                description=f"Premium quality {name}.",
                base_price=Decimal(random.randint(299, 7999)),
                gender=random.choice(["M", "W", "U"]),
                is_active=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created 100 products."
            )
        )