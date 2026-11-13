from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from shopapp.models import Product, Order


class UploadFileForm(forms.Form):
    """Форма загрузки файла с ограничением по размеру."""
    title = forms.CharField(max_length=100, label="Название файла")
    file = forms.FileField(label="Файл (не более 1 МБ)")

    def clean_file(self):
        file = self.cleaned_data["file"]
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(
                f"Файл слишком большой: {file.size} байт. "
                f"Максимум — {settings.MAX_UPLOAD_SIZE} байт (1 МБ)."
            )
        return file

class ProductForm(forms.ModelForm):
    """Форма создания продукта на основе ModelForm."""

    class Meta:
        model = Product
        fields = ["name", "description", "price", "discount", "quantity", "is_published"]

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price

    def clean_discount(self):
        discount = self.cleaned_data.get("discount", 0)
        if discount > 100:
            raise forms.ValidationError("Скидка не может превышать 100%.")
        return discount


class OrderForm(forms.ModelForm):
    """Форма создания заказа на основе ModelForm."""

    class Meta:
        model = Order
        fields = ["delivery_address", "promo_code", "user", "products"]

    def clean_promo_code(self):
        promo = self.cleaned_data.get("promo_code")
        if promo and len(promo) < 4:
            raise forms.ValidationError("Промокод должен содержать минимум 4 символа.")
        return promo

    def clean_products(self):
        products = self.cleaned_data.get("products")
        if not products:
            raise forms.ValidationError("Выберите хотя бы один товар.")
        return products

class OrderImportForm(forms.Form):
    csv_file = forms.FileField(label='CSV-файл с заказами')