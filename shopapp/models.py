from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Product(models.Model):
    """Модель товара."""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(null=False, blank=True, verbose_name="Описание")
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name="Цена"
    )
    discount = models.PositiveSmallIntegerField(
        default=0, verbose_name="Скидка, %"
    )
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    archived = models.BooleanField(default=False, verbose_name="В архиве")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse('shopapp:product_detail', kwargs={'pk': self.pk})


    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["name"]

    def __str__(self):
        return f"Product(pk={self.pk}, name={self.name!r})"


class Order(models.Model):
    """Модель заказа."""
    delivery_address = models.TextField(null=True, blank=True, verbose_name="Адрес доставки")
    promo_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Промокод")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name="Пользователь"
    )
    products = models.ManyToManyField(
        Product, related_name="orders", verbose_name="Товары"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Order(pk={self.pk}, user={self.user.username!r})"