from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Поиск через SearchFilter
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').prefetch_related('products')
    serializer_class = OrderSerializer

    # Фильтрация через DjangoFilterBackend + сортировка
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'delivery_address']   # по каким полям фильтровать
    ordering_fields = ['created_at', 'delivery_address']