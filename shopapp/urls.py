from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet, OrderViewSet

app_name = "shopapp"

router = DefaultRouter()
router.register(r'api/products', ProductViewSet, basename='api-product')
router.register(r'api/orders', OrderViewSet, basename='api-order')

urlpatterns = [
    # Главная
    path("", views.ShopIndexView.as_view(), name="index"),

    # Продукты
    path("products/", views.ProductListView.as_view(), name="products_list"),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:pk>/update/", views.ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", views.ProductArchiveView.as_view(), name="product_archive"),

    # Заказы
    path("orders/", views.OrderListView.as_view(), name="orders_list"),
    path("orders/create/", views.OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/update/", views.OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),
    path('orders/export/', views.OrdersExportView.as_view(), name='orders_export'),

    # Загрузка файла (ПР 5)
    path("upload/", views.upload_file, name="upload_file"),

    path('', include(router.urls)),
    path('products/latest/feed/', views.LatestProductsFeed(), name='latest_products_feed'),
    path('users/<int:user_id>/orders/', views.UserOrdersListView.as_view(), name='user_orders_list'),
    path('users/<int:user_id>/orders/export/', views.UserOrdersExportView.as_view(), name='user_orders_export'),
]