from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from shopapp.models import Order, Product


class Command(BaseCommand):
    help = "Создаёт тестовые заказы и связывает их с продуктами"

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="admin")

        orders_data = [
            {
                "delivery_address": "г. Москва, ул. Ленина, д. 1",
                "promo_code": "SALE10",
                "products": ["Ноутбук", "Мышь"],
            },
            {
                "delivery_address": "г. Санкт-Петербург, Невский пр., д. 10",
                "promo_code": None,
                "products": ["Смартфон", "Наушники"],
            },
            {
                "delivery_address": "г. Казань, ул. Баумана, д. 5",
                "promo_code": "NEWYEAR",
                "products": ["Клавиатура"],
            },
        ]

        for data in orders_data:
            order, created = Order.objects.get_or_create(
                delivery_address=data["delivery_address"],
                user=user,
                defaults={"promo_code": data["promo_code"]},
            )

            products = Product.objects.filter(name__in=data["products"])
            order.products.set(products)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан: {order}"))
            else:
                self.stdout.write(self.style.WARNING(f"Уже существует: {order}"))

        self.stdout.write(self.style.SUCCESS("Готово: заказы добавлены и связаны с продуктами."))
