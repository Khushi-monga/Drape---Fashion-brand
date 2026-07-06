# cart/models.py

from django.conf import settings
from django.db import models
from django.db.models import F, Sum, DecimalField
from products.models import Product
from decimal import Decimal



class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user}'s Cart"
        return f"Guest Cart ({self.pk})"

    @property
    def total_items(self):
        return (
            self.items.aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

    @property
    def subtotal(self):
        return (
            self.items.aggregate(
                total=Sum(
                    F("quantity") * F("product__base_price"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )["total"]
            or Decimal("0.00")
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_product_per_cart",
            )
        ]
    

    @property
    def unit_price(self):
        return self.product.base_price

    @property
    def subtotal(self):
        return self.product.base_price * self.quantity


    def __str__(self):
        return f"{self.quantity} × {self.product.name}"