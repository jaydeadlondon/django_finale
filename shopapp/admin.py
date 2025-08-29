from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import csv
import io

from .models import Product, Order
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Order.products.through
    extra = 0
    verbose_name = "Заказ с этим продуктом"
    verbose_name_plural = "Заказы с этим продуктом"


@admin.action(description="Архивировать выбранные продукты")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Разархивировать выбранные продукты")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price",
        "discount",
        "created_at",
        "archived",
        "orders_count",
    ]

    list_filter = [
        "archived",
        "created_at",
        "discount",
    ]

    search_fields = [
        "name",
        "description",
        "price",
    ]

    fieldsets = [
        (None, {
            "fields": ("name", "description"),
            "description": "Основная информация о продукте",
        }),

        ("Цена и скидки", {
            "fields": ("price", "discount"),
            "description": "Ценовая политика",
        }),

        ("Дополнительные опции", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Дополнительные настройки продукта",
        }),
    ]

    inlines = [
        OrderInline,
    ]

    actions = [
        mark_archived,
        mark_unarchived,
    ]

    def orders_count(self, obj: Product) -> int:
        return obj.orders.count()

    orders_count.short_description = "Количество заказов"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("orders")


class ProductInline(admin.TabularInline):
    model = Order.products.through
    extra = 1
    verbose_name = "Продукт в заказе"
    verbose_name_plural = "Продукты в заказе"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/shopapp/order/change_list.html"

    list_display = [
        "id",
        "user",
        "delivery_address_short",
        "promocode",
        "created_at",
        "products_count",
    ]

    list_filter = [
        "created_at",
        "user",
    ]

    search_fields = [
        "delivery_address",
        "promocode",
        "id",
        "user__username",
    ]

    readonly_fields = ["created_at"]

    fieldsets = [
        ("Основная информация", {
            "fields": ("user", "created_at"),
        }),

        ("Доставка", {
            "fields": ("delivery_address", "promocode"),
        }),
    ]

    inlines = [
        ProductInline,
    ]

    def delivery_address_short(self, obj: Order) -> str:
        return obj.delivery_address[:48] + "..." if len(obj.delivery_address) > 48 else obj.delivery_address

    delivery_address_short.short_description = "Адрес доставки"

    def products_count(self, obj: Order) -> int:
        return obj.products.count()

    products_count.short_description = "Количество товаров"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user").prefetch_related("products")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv),
                name='shopapp_order_import_csv',
            ),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]

                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'Файл должен иметь расширение .csv')
                    return render(request, "admin/csv_form.html", {"form": form})

                try:
                    decoded_file = csv_file.read().decode('utf-8')
                    io_string = io.StringIO(decoded_file)
                    reader = csv.DictReader(io_string)

                    created_orders = 0
                    errors = []

                    for row_num, row in enumerate(reader, start=2):
                        try:
                            delivery_address = row.get('delivery_address', '').strip()
                            promocode = row.get('promocode', '').strip()
                            user_id = row.get('user_id', '').strip()
                            product_ids = row.get('product_ids', '').strip()

                            if not delivery_address or not user_id:
                                errors.append(f"Строка {row_num}: отсутствует адрес доставки или ID пользователя")
                                continue

                            try:
                                from django.contrib.auth.models import User
                                user = User.objects.get(id=int(user_id))
                            except (User.DoesNotExist, ValueError):
                                errors.append(f"Строка {row_num}: пользователь с ID {user_id} не найден")
                                continue

                            order = Order.objects.create(
                                delivery_address=delivery_address,
                                promocode=promocode,
                                user=user
                            )

                            if product_ids:
                                try:
                                    product_id_list = [int(pid.strip()) for pid in product_ids.split(',') if
                                                       pid.strip()]
                                    products = Product.objects.filter(id__in=product_id_list)
                                    order.products.set(products)

                                    if len(products) != len(product_id_list):
                                        found_ids = list(products.values_list('id', flat=True))
                                        missing_ids = [pid for pid in product_id_list if pid not in found_ids]
                                        errors.append(f"Строка {row_num}: товары с ID {missing_ids} не найдены")
                                except ValueError:
                                    errors.append(f"Строка {row_num}: неверный формат ID товаров")

                            created_orders += 1

                        except Exception as e:
                            errors.append(f"Строка {row_num}: ошибка - {str(e)}")

                    if created_orders > 0:
                        messages.success(request, f'Успешно создано заказов: {created_orders}')

                    if errors:
                        for error in errors[:10]:
                            messages.error(request, error)
                        if len(errors) > 10:
                            messages.error(request, f'И еще {len(errors) - 10} ошибок...')

                    return redirect("admin:shopapp_order_changelist")

                except Exception as e:
                    messages.error(request, f'Ошибка при чтении файла: {str(e)}')
        else:
            form = CSVImportForm()

        return render(request, "admin/csv_form.html", {"form": form})