from decimal import Decimal
from django.core.management.base import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    help = "Создаёт тестовые продукты через get_or_create"

    def handle(self, *args, **options):
        products_data = [
            {"name": "Ноутбук", "price": Decimal("74999.99"), "quantity": 5},
            {"name": "Смартфон", "price": Decimal("42999.50"), "quantity": 10},
            {"name": "Наушники", "price": Decimal("3499.00"), "quantity": 25},
            {"name": "Клавиатура", "price": Decimal("5990.12"), "quantity": 15},
            {"name": "Мышь", "price": Decimal("1990.00"), "quantity": 30},
        ]

        for data in products_data:
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "price": data["price"],
                    "quantity": data["quantity"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан: {product}"))
            else:
                self.stdout.write(self.style.WARNING(f"Уже существует: {product}"))

        self.stdout.write(self.style.SUCCESS("Готово: продукты добавлены."))
