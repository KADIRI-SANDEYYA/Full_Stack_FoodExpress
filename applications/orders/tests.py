from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from applications.orders.models import Order
from applications.restaurants.models import Category, FoodItem, Restaurant


class CartAndCheckoutRenderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="strong-pass-123",
        )
        self.restaurant = Restaurant.objects.create(
            name="Green Bowl",
            logo="restaurants/logos/green-bowl.jpg",
            cuisine_type="Healthy",
            address="42 Garden Road",
            rating=4.4,
            delivery_time=25,
            is_open=True,
        )
        self.category = Category.objects.create(name="Salads", is_active=True)
        self.food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Paneer Salad",
            description="Fresh greens and grilled paneer.",
            price=199,
            is_veg=True,
            is_available=True,
            rating=4.2,
        )

    def test_cart_actions_and_checkout_render(self):
        add_response = self.client.post(reverse("add_to_cart", args=[self.food.id]))
        self.assertEqual(add_response.status_code, 302)

        cart_response = self.client.get(reverse("cart"))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, "Paneer Salad")

        self.client.force_login(self.user)
        checkout_response = self.client.get(reverse("checkout"))
        self.assertEqual(checkout_response.status_code, 200)

    @patch("applications.orders.views.create_razorpay_order")
    def test_checkout_creates_pending_order_and_redirects_to_payment(self, mock_create_order):
        self.client.force_login(self.user)
        self.client.post(reverse("add_to_cart", args=[self.food.id]))
        mock_create_order.return_value = {
            "id": "order_123",
            "amount": 19900,
            "currency": "INR",
        }

        response = self.client.post(
            reverse("checkout"),
            {"address": "123 Main Street, Delhi", "phone": "9876543210"},
        )

        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        self.assertRedirects(response, reverse("payment", args=[order.id]))
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.razorpay_order_id, "order_123")
