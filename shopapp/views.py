from django.core.exceptions import PermissionDenied
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache
from django.core import serializers
from .models import Product, Order
from .forms import ProductForm, OrderForm
from django.utils.translation import gettext_lazy as _
from django.contrib.syndication.views import Feed
import json


def shop_index(request):
    """Главная страница магазина со списком ссылок"""
    context = {
        'title': _('Shop'),
        'pages': [
            {'name': _('Product list'), 'url': 'products_list'},
            {'name': _('Order list'), 'url': 'orders_list'},
        ]
    }
    return render(request, 'shopapp/shop_index.html', context)


class ProductListView(ListView):
    """Отображение списка продуктов"""
    model = Product
    template_name = 'shopapp/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(archived=False)


class ProductDetailView(DetailView):
    """Отображение деталей продукта"""
    model = Product
    template_name = 'shopapp/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создание нового продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/product_form.html'
    success_url = reverse_lazy('shopapp:products_list')
    permission_required = 'shopapp.add_product'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/product_form.html'

    def test_func(self):
        """Проверка прав на редактирование"""
        product = self.get_object()
        user = self.request.user

        if user.is_superuser:
            return True

        return (
                user.has_perm('shopapp.change_product') and
                product.created_by == user
        )

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для редактирования этого продукта")

    def get_success_url(self):
        return reverse('shopapp:product_detail', kwargs={'pk': self.object.pk})


class ProductArchiveView(View):
    """Архивация продукта (soft delete)"""

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        context = {
            'product': product,
            'title': 'Архивировать продукт'
        }
        return render(request, 'shopapp/product_confirm_archive.html', context)

    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        product.archived = True
        product.save()
        return HttpResponseRedirect(reverse('shopapp:products_list'))


class OrderListView(ListView):
    """Отображение списка заказов"""
    model = Order
    template_name = 'shopapp/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('products')


class OrderDetailView(DetailView):
    """Отображение деталей заказа"""
    model = Order
    template_name = 'shopapp/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related('products')


class OrderCreateView(CreateView):
    """Создание нового заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'shopapp/order_form.html'
    success_url = reverse_lazy('shopapp:orders_list')


class OrderUpdateView(UpdateView):
    """Обновление заказа"""
    model = Order
    form_class = OrderForm
    template_name = 'shopapp/order_form.html'

    def get_success_url(self):
        return reverse('shopapp:order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(DeleteView):
    """Полное удаление заказа"""
    model = Order
    template_name = 'shopapp/order_confirm_delete.html'
    success_url = reverse_lazy('shopapp:orders_list')


class OrdersExportView(UserPassesTestMixin, View):
    """Экспорт заказов в JSON"""

    def test_func(self):
        """Проверка доступа - только для staff"""
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        """Возвращает JSON со всеми заказами"""
        orders = Order.objects.select_related('user').prefetch_related('products').all()
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': list(order.products.values_list('pk', flat=True))
            })
        return JsonResponse({
            'orders': orders_data
        })


class UserOrdersListView(LoginRequiredMixin, ListView):
    """Список заказов конкретного пользователя с кешированием"""
    template_name = 'shopapp/user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        self.owner = get_object_or_404(User, pk=user_id)
        return Order.objects.filter(user=self.owner).select_related('user').prefetch_related('products').order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


def user_orders_export(request, user_id):
    """Экспорт заказов пользователя в JSON с низкоуровневым кешированием"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    cache_key = f"user_orders_export_{user_id}"

    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data, safe=False)

    owner = get_object_or_404(User, pk=user_id)
    orders = Order.objects.filter(user=owner).select_related('user').prefetch_related('products').order_by('pk')

    orders_data = []
    for order in orders:
        order_data = {
            'id': order.pk,
            'delivery_address': order.delivery_address,
            'promocode': order.promocode,
            'created_at': order.created_at.isoformat(),
            'user': {
                'id': order.user.pk,
                'username': order.user.username,
                'first_name': order.user.first_name,
                'last_name': order.user.last_name,
            },
            'products': [
                {
                    'id': product.pk,
                    'name': product.name,
                    'price': str(product.price),
                    'discount': product.discount,
                }
                for product in order.products.all()
            ]
        }
        orders_data.append(order_data)

    cache.set(cache_key, orders_data, 300)

    return JsonResponse(orders_data, safe=False)


class LatestProductsFeed(Feed):
    title = "Последние товары"
    link = reverse_lazy("shopapp:products_list")
    description = "Новые товары в нашем магазине"

    def items(self):
        return Product.objects.filter(archived=False).order_by('-created_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.created_at