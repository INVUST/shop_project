from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission

from shopapp.models import Order, Product


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testorder',
            password='StrongPass123!',
        )
        permission = Permission.objects.get(codename='view_order')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='ул. Ленина, 1',
            promo_code='TEST123',
            user=self.user,
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        url = reverse('shopapp:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)

        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promo_code)
        self.assertEqual(response.context['object'].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = ['users.json', 'products.json', 'orders.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='staffuser',
            password='StrongPass123!',
            is_staff=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_export(self):
        url = reverse('shopapp:orders_export')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        expected_orders = [
            {
                'id': order.pk,
                'address': order.delivery_address,
                'promocode': order.promo_code,
                'user_id': order.user_id,
                'products': [p.pk for p in order.products.all()],
            }
            for order in (
                Order.objects
                .select_related('user')
                .prefetch_related('products')
                .order_by('pk')
            )
        ]

        self.assertEqual(data, {'orders': expected_orders})