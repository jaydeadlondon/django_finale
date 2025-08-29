from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order, Product


class Command(BaseCommand):
    help = "Создаёт тестовые заказы"

    def handle(self, *args, **options):
        self.stdout.write("Создаём заказы...")

        user, _ = User.objects.get_or_create(
            username="testuser",
            defaults={
                "first_name": "Тест",
                "last_name": "Пользователь",
                "email": "test@example.com",
            }
        )

        products = Product.objects.filter(archived=False)

        if not products.exists():
            self.stdout.write(self.style.ERROR("Сначала создайте продукты!"))
            return

        order1, created1 = Order.objects.get_or_create(
            delivery_address="Москва, ул. Пушкина, д. 10",
            user=user,
            defaults={"promocode": "SALE10"}
        )

        if created1:
            order1.products.set(products[:2])
            self.stdout.write(f"Создан заказ #{order1.pk}")

        order2, created2 = Order.objects.get_or_create(
            delivery_address="Санкт-Петербург, Невский пр., д. 1",
            user=user,
        )

        if created2:
            order2.products.set(products)
            self.stdout.write(f"Создан заказ #{order2.pk}")

        self.stdout.write(self.style.SUCCESS("Заказы созданы!"))