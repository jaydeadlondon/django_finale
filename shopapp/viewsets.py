from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Получить список продуктов",
        description="Возвращает список всех продуктов с возможностью поиска и сортировки"
    ),
    create=extend_schema(
        summary="Создать новый продукт",
        description="Создает новый продукт в системе"
    ),
    retrieve=extend_schema(
        summary="Получить продукт по ID",
        description="Возвращает детальную информацию о продукте"
    ),
    update=extend_schema(
        summary="Обновить продукт",
        description="Полное обновление информации о продукте"
    ),
    partial_update=extend_schema(
        summary="Частично обновить продукт",
        description="Частичное обновление информации о продукте"
    ),
    destroy=extend_schema(
        summary="Удалить продукт",
        description="Удаляет продукт из системы"
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с продуктами.

    Поддерживает:
    - Поиск по названию и описанию
    - Сортировку по названию, цене и дате создания
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="Получить список заказов",
        description="Возвращает список всех заказов с возможностью фильтрации и сортировки"
    ),
    create=extend_schema(
        summary="Создать новый заказ",
        description="Создает новый заказ в системе"
    ),
    retrieve=extend_schema(
        summary="Получить заказ по ID",
        description="Возвращает детальную информацию о заказе"
    ),
    update=extend_schema(
        summary="Обновить заказ",
        description="Полное обновление информации о заказе"
    ),
    partial_update=extend_schema(
        summary="Частично обновить заказ",
        description="Частичное обновление информации о заказе"
    ),
    destroy=extend_schema(
        summary="Удалить заказ",
        description="Удаляет заказ из системы"
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с заказами.

    Поддерживает:
    - Фильтрацию по пользователю, промокоду и дате создания
    - Сортировку по дате создания и пользователю
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    filterset_fields = ['user', 'promocode', 'created_at']
    ordering_fields = ['created_at', 'user']
    ordering = ['-created_at']