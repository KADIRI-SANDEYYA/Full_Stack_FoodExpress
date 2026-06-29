from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, FoodItem, Restaurant


class PageRenderTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Urban Tandoor",
            logo="restaurants/logos/urban-tandoor.jpg",
            cover_image="restaurants/covers/urban-tandoor.jpg",
            description="North Indian meals and quick delivery.",
            cuisine_type="Indian",
            address="12 Market Street",
            rating=4.5,
            delivery_time=30,
            is_open=True,
        )
        self.category = Category.objects.create(name="Biryani", is_active=True)
        self.food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Chicken Biryani",
            image="foods/chicken-biryani.jpg",
            description="Aromatic rice with slow-cooked chicken.",
            price=249,
            is_veg=False,
            is_available=True,
            rating=4.6,
        )

    def test_public_pages_render(self):
        urls = [
            reverse("home"),
            reverse("restaurants"),
            reverse("food_list", args=[self.restaurant.id]),
            reverse("single_food", args=[self.food.id]),
            reverse("cart"),
            reverse("login"),
            reverse("register"),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_manager_dashboard_renders_for_staff(self):
        staff = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="strong-pass-123",
            is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.get(reverse("manager_dashboard"))

        self.assertEqual(response.status_code, 200)
