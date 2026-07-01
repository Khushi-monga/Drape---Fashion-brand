from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    GENDER_CHOICES = [
        ("M", "Men"),
        ("W", "Women"),
        ("U", "Unisex"),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True, max_length=255)

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default="U"
    )

    sku = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Unique Stock Keeping Unit for this product."
    )

    search_tags = models.TextField(
        blank=True,
        db_index=True,
        help_text="Comma-separated keywords for improving search."
    )

    search_vector = SearchVectorField(
        null=True,
        blank=True,
        editable=False,
        db_index=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]

    def __str__(self):
        return self.name


class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    size = models.CharField(
        max_length=20,
        blank=True
    )

    color = models.CharField(
        max_length=50,
        blank=True
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True
    )

    is_primary = models.BooleanField(default=False)

    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.product.name}"