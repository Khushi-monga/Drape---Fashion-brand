from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )


    # -------------------------
    # Shipping Address Snapshot
    # -------------------------

    full_name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=20
    )

    address_line_1 = models.CharField(
        max_length=255
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    postal_code = models.CharField(
        max_length=20
    )

    country = models.CharField(
        max_length=100,
        default="India"
    )


    # -------------------------
    # Price Details
    # -------------------------

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    # -------------------------
    # Order Status
    # -------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )


    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )


    # -------------------------
    # Timestamps
    # -------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = [
            "-created_at"
        ]


    def __str__(self):
        return f"Order #{self.id} - {self.user}"



class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )


    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )


    # Product snapshot
    product_name = models.CharField(
        max_length=255
    )


    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    quantity = models.PositiveIntegerField(
        default=1
    )


    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:
        ordering = [
            "id"
        ]


    def __str__(self):
        return f"{self.product_name} x {self.quantity}"