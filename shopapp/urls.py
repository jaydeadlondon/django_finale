from django.urls import path, include
from . import views
from .viewsets import ProductViewSet, OrderViewSet
from rest_framework.routers import DefaultRouter
from .views import LatestProductsFeed

app_name = 'shopapp'

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', views.shop_index, name='index'),

    path('products/', views.ProductListView.as_view(), name='products_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive/', views.ProductArchiveView.as_view(), name='product_archive'),

    path('orders/', views.OrderListView.as_view(), name='orders_list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('orders/export/', views.OrdersExportView.as_view(), name='orders_export'),

    path('users/<int:user_id>/orders/', views.UserOrdersListView.as_view(), name='user_orders'),
    path('users/<int:user_id>/orders/export/', views.user_orders_export, name='user_orders_export'),

    path('products/latest/feed/', LatestProductsFeed(), name='products_feed'),

    path('api/', include(router.urls)),
]