from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Product, Order
import json
import os


class Command(BaseCommand):
    help = 'Создаёт тестовые фикстуры для тестов'

    def handle(self, *args, **options):
        fixtures_dir = 'shopapp/fixtures'
        os.makedirs(fixtures_dir, exist_ok=True)

        users_data = [
            {
                "model": "auth.user",
                "pk": 100,
                "fields": {
                    "username": "fixture_user1",
                    "email": "fixture1@test.com",
                    "password": "pbkdf2_sha256$260000$test$test",
                    "is_staff": False,
                    "is_active": True,
                    "is_superuser": False,
                    "first_name": "Test",
                    "last_name": "User"
                }
            },
            {
                "model": "auth.user",
                "pk": 101,
                "fields": {
                    "username": "fixture_user2",
                    "email": "fixture2@test.com",
                    "password": "pbkdf2_sha256$260000$test$test",
                    "is_staff": False,
                    "is_active": True,
                    "is_superuser": False,
                    "first_name": "Another",
                    "last_name": "User"
                }
            }
        ]

        products_data = [
            {
                "model": "shopapp.product",
                "pk": 100,
                "fields": {
                    "name": "Fixture Product 1",
                    "description": "Test product from fixture",
                    "price": "999.99",
                    "discount": 10,
                    "created_at": "2024-01-01T10:00:00Z",
                    "archived": False,
                    "created_by": 100
                }
            },
            {
                "model": "shopapp.product",
                "pk": 101,
                "fields": {
                    "name": "Fixture Product 2",
                    "description": "Another test product",
                    "price": "1999.99",
                    "discount": 0,
                    "created_at": "2024-01-01T11:00:00Z",
                    "archived": False,
                    "created_by": 100
                }
            },
            {
                "model": "shopapp.product",
                "pk": 102,
                "fields": {
                    "name": "Fixture Product 3",
                    "description": "Third test product",
                    "price": "2999.99",
                    "discount": 15,
                    "created_at": "2024-01-01T12:00:00Z",
                    "archived": False,
                    "created_by": 101
                }
            }
        ]

        orders_data = [
            {
                "model": "shopapp.order",
                "pk": 100,
                "fields": {
                    "delivery_address": "Fixture Address 1, Moscow",
                    "promocode": "FIXTURE10",
                    "created_at": "2024-01-02T10:00:00Z",
                    "user": 100,
                    "products": [100, 101]
                }
            },
            {
                "model": "shopapp.order",
                "pk": 101,
                "fields": {
                    "delivery_address": "Fixture Address 2, St. Petersburg",
                    "promocode": "FIXTURE20",
                    "created_at": "2024-01-02T11:00:00Z",
                    "user": 101,
                    "products": [101, 102]
                }
            },
            {
                "model": "shopapp.order",
                "pk": 102,
                "fields": {
                    "delivery_address": "Fixture Address 3, Kazan",
                    "promocode": "",
                    "created_at": "2024-01-02T12:00:00Z",
                    "user": 100,
                    "products": [102]
                }
            }
        ]

        with open(os.path.join(fixtures_dir, 'users-fixtures.json'), 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)

        with open(os.path.join(fixtures_dir, 'products-fixtures.json'), 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)

        with open(os.path.join(fixtures_dir, 'orders-fixtures.json'), 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS('Фикстуры успешно созданы!'))