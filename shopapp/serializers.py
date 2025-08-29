from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'discount',
            'created_at',
            'archived',
            'created_by',
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'delivery_address',
            'promocode',
            'created_at',
            'user',
            'products',
        ]