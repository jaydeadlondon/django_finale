from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))
    discount = models.PositiveSmallIntegerField(default=0, verbose_name=_("Discount"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    archived = models.BooleanField(default=False, verbose_name=_("Archived"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_products',
        verbose_name=_("Created by"),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]
        permissions = [
            ("can_create_product", _("Can create product")),
        ]

    def __str__(self):
        return f"{self.name} - {self.price}₽"

    def get_absolute_url(self):
        return f"/shop/products/{self.pk}/"


class Order(models.Model):
    delivery_address = models.TextField(verbose_name=_("Delivery address"))
    promocode = models.CharField(max_length=20, blank=True, verbose_name=_("Promo code"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("User"))
    products = models.ManyToManyField(Product, related_name="orders", verbose_name=_("Products"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} from {self.user.username}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Product")
    )
    image = models.ImageField(upload_to='products/', verbose_name=_("Image"))
    description = models.CharField(max_length=200, blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")