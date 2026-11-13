from rest_framework import serializers
from .models import Product, Order



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'delivery_address', 'promo_code', 'user_id', 'products')