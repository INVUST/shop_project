from django.contrib import admin
from django.utils.translation import ngettext
from django.contrib import messages
from shopapp.models import Product, Order
import csv
from django.urls import path
from django.shortcuts import render, redirect
from .forms import OrderImportForm


# ---------- Inline для отображения заказов на странице продукта ----------
class OrderInline(admin.TabularInline):
    model = Order.products.through
    extra = 0
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы с этим товаром"


# ---------- Групповое действие: архивация ----------
@admin.action(description="Архивировать выбранные товары")
def archive_products(modeladmin, request, queryset):
    updated = queryset.update(archived=True)
    modeladmin.message_user(
        request,
        ngettext("%d товар архивирован.", "%d товаров архивировано.", updated) % updated,
        messages.SUCCESS,
    )


@admin.action(description="Снять с архива")
def unarchive_products(modeladmin, request, queryset):
    updated = queryset.update(archived=False)
    modeladmin.message_user(
        request,
        ngettext("%d товар разархивирован.", "%d товаров разархивировано.", updated) % updated,
        messages.SUCCESS,
    )


# ---------- ProductAdmin ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "discount", "quantity", "is_published", "archived", "created_at")
    list_filter = ("is_published", "archived", "created_at")
    search_fields = ("name", "price")
    list_editable = ("is_published", "archived")
    ordering = ("name",)
    actions = [archive_products, unarchive_products]
    inlines = [OrderInline]

    fieldsets = (
        (None, {"fields": ("name", "description")}),
        ("Цена", {"fields": ("price", "discount")}),
        ("Дополнительные опции", {
            "fields": ("is_published", "archived"),
            "classes": ("collapse",),
        }),
    )


# ---------- OrderAdmin ----------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "delivery_address", "promo_code", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("delivery_address", "promo_code", "user__username")
    raw_id_fields = ("user",)
    filter_horizontal = ("products",)
    date_hierarchy = "created_at"
    change_list_template = "shopapp/orders_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv, name="shopapp_order_import_csv"),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = OrderImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                decoded = csv_file.read().decode("utf-8")
                reader = csv.DictReader(decoded.splitlines())
                count = 0
                for row in reader:
                    product_ids = [int(pid) for pid in row["product_ids"].split("|") if pid]
                    order = Order.objects.create(
                        user_id=int(row["user_id"]),
                        delivery_address=row["delivery_address"],
                        promo_code=row.get("promo_code", ""),
                    )
                    order.products.set(product_ids)
                    count += 1
                self.message_user(
                    request,
                    f"Импортировано заказов: {count}",
                    messages.SUCCESS,
                )
                return redirect("admin:shopapp_order_changelist")
        else:
            form = OrderImportForm()
        return render(request, "admin/csv_form.html", {"form": form})