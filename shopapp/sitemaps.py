from django.contrib.sitemaps import Sitemap
from .models import Product


class ShopSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(archived=False)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f"/shop/products/{obj.pk}/"