import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from products.models import Product, Brand, Category

from products.seed_data.brands import BRANDS
from products.seed_data.clothing import CLOTHING
from products.seed_data.footwear import FOOTWEAR
from products.seed_data.accessories import ACCESSORIES


CATEGORY_MAP = {
    "Clothing": CLOTHING,
    "Footwear": FOOTWEAR,
    "Accessories": ACCESSORIES,
}


# class Command(BaseCommand):
#     help = "Seed products with generated fashion data"

#     def handle(self, *args, **options):
#         self.stdout.write("Starting seeding...")

#         self.create_brands()
#         self.create_products()

#         self.stdout.write(self.style.SUCCESS("Seeding completed."))

#     # -------------------------
#     # Step 1: Create brands
#     # -------------------------
#     def create_brands(self):
#         self.stdout.write("Creating brands...")

#         for name in BRANDS:
#             Brand.objects.get_or_create(name=name)

#         self.stdout.write(self.style.SUCCESS("Brands ready."))

#     # -------------------------
#     # Step 2: Create products
#     # -------------------------
#     def create_products(self):
#         self.stdout.write("Creating products...")

#         for category_name, dataset in CATEGORY_MAP.items():

#             category = Category.objects.get(name=category_name)

#             for product_type, config in dataset.items():

#                 # generate multiple products per type
#                 for _ in range(10):  # adjust later (10 per type for now)

#                     brand = Brand.objects.order_by("?").first()

#                     material = random.choice(config["materials"])
#                     fit = random.choice(config.get("fits", [""])) or ""
#                     style = random.choice(config.get("styles", [""])) or ""
#                     gender = random.choice(config["genders"])

#                     name = f"{fit} {style} {material} {product_type}".replace("  ", " ").strip()

#                     base_price = random.randint(
#                         config["price_range"][0],
#                         config["price_range"][1]
#                     )

#                     sku = self.generate_sku(brand.name, product_type)

#                     tags = config["tags"] + [
#                         material.lower(),
#                         fit.lower(),
#                         style.lower(),
#                         product_type.lower(),
#                         brand.name.lower(),
#                     ]

#                     base_slug = slugify(f"{brand.name}-{name}")

#                     slug = base_slug[:140]  # keep safe for DB

#                     Product.objects.create(
#                         category=category,
#                         brand=brand,
#                         name=name,
#                         slug=slug,
#                         sku=sku,
#                         description=f"{name} designed for everyday comfort and modern style.",
#                         base_price=base_price,
#                         gender=gender,
#                         search_tags=",".join(tags),
#                         is_active=True,
#                     )

#         self.stdout.write(self.style.SUCCESS("Products created."))

#     # -------------------------
#     # Step 3: SKU generator
#     # -------------------------
#     def generate_sku(self, brand, product_type):
#         prefix = brand[:3].upper()
#         type_code = product_type[:3].upper()
#         number = random.randint(1000, 9999)

#         return f"{prefix}-{type_code}-{number}"
    



# import random
# from django.core.management.base import BaseCommand
# from django.utils.text import slugify

# from products.models import Product, Brand, Category

# from products.seed_data.brands import BRANDS
# from products.seed_data.clothing import CLOTHING
# from products.seed_data.footwear import FOOTWEAR
# from products.seed_data.accessories import ACCESSORIES


# CATEGORY_MAP = {
#     "Clothing": CLOTHING,
#     "Footwear": FOOTWEAR,
#     "Accessories": ACCESSORIES,
# }


class Command(BaseCommand):
    help = "Seed products safely (idempotent + duplicate-safe)"

    def handle(self, *args, **options):
        self.stdout.write("Starting seeding...")

        self.create_brands()
        self.create_products()

        self.stdout.write(self.style.SUCCESS("Seeding completed."))

    # -------------------------
    # BRANDS
    # -------------------------
    def create_brands(self):
        self.stdout.write("Creating brands...")

        for name in BRANDS:
            Brand.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("Brands ready."))

    # -------------------------
    # PRODUCTS
    # -------------------------
    def create_products(self):
        self.stdout.write("Creating products...")

        brands = list(Brand.objects.all())

        for category_name, dataset in CATEGORY_MAP.items():

            category = Category.objects.get(name=category_name)

            for product_type, config in dataset.items():

                for _ in range(10):

                    brand = random.choice(brands)

                    material = random.choice(config["materials"])
                    fit = random.choice(config.get("fits", [""])) or ""
                    style = random.choice(config.get("styles", [""])) or ""
                    gender = random.choice(config["genders"])

                    name = f"{fit} {style} {material} {product_type}".replace("  ", " ").strip()

                    base_price = random.randint(
                        config["price_range"][0],
                        config["price_range"][1]
                    )

                    sku = self.generate_sku(brand.name)

                    base_slug = slugify(f"{brand.name}-{name}")
                    slug = self.generate_unique_slug(base_slug)

                    tags = list(set(
                        config["tags"]
                        + [material, fit, style, product_type, brand.name]
                    ))

                    Product.objects.get_or_create(
                        sku=sku,
                        defaults={
                            "category": category,
                            "brand": brand,
                            "name": name,
                            "slug": slug[:140],
                            "description": f"{name} designed for everyday wear and modern style.",
                            "base_price": base_price,
                            "gender": gender,
                            "search_tags": " ".join([t.lower() for t in tags]),
                            "is_active": True,
                        }
                    )

        self.stdout.write(self.style.SUCCESS("Products ready."))

    # -------------------------
    # SKU GENERATOR (SAFE)
    # -------------------------
    def generate_sku(self, brand):
        while True:
            sku = f"{brand[:3].upper()}-{random.randint(100000, 999999)}"
            if not Product.objects.filter(sku=sku).exists():
                return sku

    # -------------------------
    # SLUG GENERATOR (SAFE)
    # -------------------------
    def generate_unique_slug(self, base_slug):
        slug = base_slug[:140]
        counter = 1

        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug[:135]}-{counter}"
            counter += 1

        return slug