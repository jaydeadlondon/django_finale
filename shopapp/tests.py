from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.contrib.auth.models import Group
import json

from .models import Product, Order


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.login(username='testuser', password='testpass123')

        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=100.00,
            discount=10,
            created_by=self.user
        )

        self.order = Order.objects.create(
            user=self.user,
            delivery_address='Test Address, 123',
            promocode='TESTCODE'
        )
        self.order.products.add(self.product)

    def tearDown(self):
        self.order.delete()
        self.product.delete()

    def test_order_details(self):
        """Тест получения деталей заказа"""
        url = reverse('shopapp:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertEqual(response.context['order'].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    """Тесты для экспорта заказов"""

    fixtures = [
        'users-fixtures.json',
        'products-fixtures.json',
        'orders-fixtures.json'
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpass123',
            email='staff@example.com',
            is_staff=True
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем пользователя"""
        cls.staff_user.delete()
        super().tearDownClass()

    def setUp(self):
        """Логинимся перед каждым тестом"""
        self.client.login(username='staffuser', password='staffpass123')

    def test_orders_export(self):
        """Тест экспорта заказов в JSON"""
        url = reverse('shopapp:orders_export')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response['Content-Type'], 'application/json')

        response_data = json.loads(response.content)

        self.assertIn('orders', response_data)
        self.assertIsInstance(response_data['orders'], list)

        orders_from_db = Order.objects.select_related('user').prefetch_related('products').all()

        expected_data = {
            'orders': []
        }

        for order in orders_from_db:
            expected_data['orders'].append({
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': list(order.products.values_list('pk', flat=True))
            })

        self.assertEqual(response_data, expected_data)

        if response_data['orders']:
            first_order = response_data['orders'][0]
            required_fields = ['id', 'delivery_address', 'promocode', 'user_id', 'product_ids']
            for field in required_fields:
                self.assertIn(field, first_order, f"Поле {field} отсутствует в экспорте заказа")

            self.assertIsInstance(first_order['id'], int)
            self.assertIsInstance(first_order['delivery_address'], str)
            self.assertIsInstance(first_order['promocode'], (str, type(None)))
            self.assertIsInstance(first_order['user_id'], int)
            self.assertIsInstance(first_order['product_ids'], list)

    def test_orders_export_requires_staff(self):
        """Тест, что обычный пользователь не может экспортировать"""
        regular_user = User.objects.create_user(
            username='regular',
            password='pass123'
        )

        self.client.login(username='regular', password='pass123')

        url = reverse('shopapp:orders_export')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

        regular_user.delete()