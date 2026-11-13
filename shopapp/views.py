from django.views.generic import (
    TemplateView,
    View,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
    LoginRequiredMixin,
)
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Product, Order
from .forms import ProductForm, OrderForm
from django.http import JsonResponse

from django.contrib.syndication.views import Feed
from django.urls import reverse

from django.views.generic import ListView

from django.core.cache import cache
from django.views import View
from .serializers import OrderExportSerializer



# ==================== ГЛАВНАЯ (TemplateView) ====================
class ShopIndexView(TemplateView):
    """Главная страница магазина со ссылками."""
    template_name = "shopapp/shop_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["links"] = [
            {"title": "Каталог товаров", "url_name": "shopapp:products_list"},
            {"title": "Список заказов", "url_name": "shopapp:orders_list"},
            {"title": "Создать продукт", "url_name": "shopapp:product_create"},
            {"title": "Создать заказ", "url_name": "shopapp:order_create"},
            {"title": "Загрузить файл", "url_name": "shopapp:upload_file"},
            {"title": "Админка", "url_name": "admin:index"},
        ]
        return context


# ==================== ПРОДУКТЫ ====================
class ProductListView(ListView):
    """Список неархивированных продуктов."""
    model = Product
    template_name = "shopapp/product_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return Product.objects.filter(archived=False)


class ProductDetailView(DetailView):
    """Детали выбранного продукта."""
    model = Product
    template_name = "shopapp/product_detail.html"
    context_object_name = "object"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/product_form.html'
    success_url = '/shop/products/'
    permission_required = 'shopapp.add_product'
    raise_exception = True

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shopapp/product_form.html'
    success_url = '/shop/products/'

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        product = self.get_object()
        return user.has_perm('shopapp.change_product') and product.created_by == user


class ProductArchiveView(DeleteView):
    """Soft delete: GET — подтверждение, POST — архивация."""
    model = Product
    template_name = "shopapp/product_confirm_archive.html"
    success_url = reverse_lazy("shopapp:products_list")
    context_object_name = "object"

    def form_valid(self, form):
        """Вместо удаления — устанавливаем archived=True."""
        self.object = self.get_object()
        self.object.archived = True
        self.object.save()
        return redirect(self.get_success_url())


# ==================== ЗАКАЗЫ ====================
class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/user_orders_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
        return (
            Order.objects
            .filter(user=self.owner)
            .select_related('user')
            .prefetch_related('products')
            .order_by('pk')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context

class OrderDetailView(DetailView):
    """Детали заказа."""
    model = Order
    template_name = "shopapp/order_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("user")
            .prefetch_related("products")
        )


class OrderCreateView(CreateView):
    """Создание заказа."""
    model = Order
    form_class = OrderForm
    template_name = "shopapp/order_form.html"
    success_url = reverse_lazy("shopapp:orders_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать заказ"
        return context


class OrderUpdateView(UpdateView):
    """Редактирование заказа."""
    model = Order
    form_class = OrderForm
    template_name = "shopapp/order_form.html"
    success_url = reverse_lazy("shopapp:orders_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать заказ #{self.object.pk}"
        return context


class OrderDeleteView(DeleteView):
    """Hard delete: GET — подтверждение, POST — удаление."""
    model = Order
    template_name = "shopapp/order_confirm_delete.html"
    success_url = reverse_lazy("shopapp:orders_list")
    context_object_name = "object"

class OrdersExportView(UserPassesTestMixin, View):
    """Экспорт всех заказов в JSON. Доступ только для is_staff."""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        orders = (
            Order.objects
            .select_related('user')
            .prefetch_related('products')
        )
        data = {
            'orders': [
                {
                    'id': order.pk,
                    'address': order.delivery_address,
                    'promocode': order.promo_code,
                    'user_id': order.user_id,
                    'products': [p.pk for p in order.products.all()],
                }
                for order in orders
            ]
        }
        return JsonResponse(data)



def upload_file(request):
    """Загрузка файла с ограничением размера 1 МБ."""
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
                messages.error(request, "Файл превышает 1 МБ — загрузка отменена.")
                return render(request, "shopapp/upload_file.html", {"form": form})
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(uploaded_file.name, uploaded_file)
            messages.success(request, f"Файл «{filename}» успешно загружен.")
            return redirect("shopapp:upload_file")
        else:
            messages.error(request, "Исправьте ошибки формы.")
    else:
        form = UploadFileForm()
    return render(request, "shopapp/upload_file.html", {"form": form})

class LatestProductsFeed(Feed):
    title = "Последние продукты"
    link = "/shop/products/"
    description = "Последние добавленные продукты магазина"

    def items(self):
        return Product.objects.filter(archived=False).order_by('-created_at')[:10]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse('shopapp:product_detail', kwargs={'pk': item.pk})

class UserOrdersExportView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        owner = get_object_or_404(User, pk=user_id)

        cache_key = f'user_orders_export_{owner.pk}'
        cached = cache.get(cache_key)

        if cached is not None:
            return JsonResponse({'orders': cached})

        orders = (
            Order.objects
            .filter(user=owner)
            .prefetch_related('products')
            .order_by('pk')
        )
        data = OrderExportSerializer(orders, many=True).data
        cache.set(cache_key, data, 300)

        return JsonResponse({'orders': data})

class OrderListView(ListView):
    """Список заказов с пользователями и продуктами."""
    model = Order
    template_name = "shopapp/order_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("user")
            .prefetch_related("products")
        )