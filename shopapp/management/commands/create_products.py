from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    help = "Создаёт тестовые продукты"

    def handle(self, *args, **options):
        self.stdout.write("Создаём продукты...")

        products_data = [
            {
                "name": "Ноутбук",
                "description": "Мощный ноутбук для работы и игр",
                "price": 75000,
                "discount": 10,
            },
            {
                "name": "Смартфон",
                "description": "Современный смартфон с отличной камерой",
                "price": 45000,
                "discount": 5,
            },
            {
                "name": "Наушники",
                "description": "Беспроводные наушники с шумоподавлением",
                "price": 15000,
                "discount": 0,
            },
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults=product_data
            )
            if created:
                self.stdout.write(f"Создан продукт: {product.name}")
            else:
                self.stdout.write(f"Продукт уже существует: {product.name}")

        self.stdout.write(self.style.SUCCESS("Продукты созданы!"))