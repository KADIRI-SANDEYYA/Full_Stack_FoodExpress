from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from applications.restaurants.models import Category, FoodItem, Restaurant


class Command(BaseCommand):
    help = "Create demo restaurants, categories, food items, and an admin user."

    def handle(self, *args, **options):
        categories = [
            ("Biryani", "Aromatic rice dishes with rich spices."),
            ("Pizza", "Fresh pizzas with classic toppings."),
            ("Fast Food", "Quick bites, burgers, and snacks."),
            ("Beverages", "Cold drinks, shakes, and coffees."),
            ("Desserts", "Sweet treats for every meal."),
        ]
        category_map = {}
        for name, description in categories:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={"description": description, "is_active": True},
            )
            category_map[name] = category

        restaurants = [
            {
                "name": "Paradise Biryani",
                "cuisine_type": "Biryani, North Indian",
                "address": "HITEC City Road, Hyderabad",
                "rating": Decimal("4.5"),
                "delivery_time": 30,
                "description": "Popular Hyderabad-style biryani and kebab restaurant.",
            },
            {
                "name": "Domino's Pizza",
                "cuisine_type": "Pizza, Italian, Fast Food",
                "address": "KPHB Colony, Hyderabad",
                "rating": Decimal("4.3"),
                "delivery_time": 25,
                "description": "Freshly baked pizzas and sides.",
            },
            {
                "name": "Starbucks",
                "cuisine_type": "Coffee, Cafe, Desserts",
                "address": "Madhapur Main Road, Hyderabad",
                "rating": Decimal("4.4"),
                "delivery_time": 20,
                "description": "Coffee, sandwiches, frappes, and desserts.",
            },
            {
                "name": "Shah Ghouse",
                "cuisine_type": "Biryani, Mughlai, Chinese",
                "address": "Gachibowli, Hyderabad",
                "rating": Decimal("4.6"),
                "delivery_time": 35,
                "description": "Famous biryani, shawarma, and non-veg starters.",
            },
        ]
        restaurant_map = {}
        for data in restaurants:
            restaurant, _ = Restaurant.objects.get_or_create(
                name=data["name"],
                defaults={**data, "is_open": True},
            )
            restaurant_map[data["name"]] = restaurant

        foods = [
            ("Hyderabadi Mutton Biryani", "Paradise Biryani", "Biryani", "Tender mutton with fragrant basmati rice.", "349.00", False, "4.7"),
            ("Chicken Tandoori", "Paradise Biryani", "Fast Food", "Smoky grilled chicken with Indian spices.", "279.00", False, "4.4"),
            ("Veg Fried Rice", "Shah Ghouse", "Fast Food", "Classic rice tossed with vegetables.", "159.00", True, "4.1"),
            ("Chicken Shawarma", "Shah Ghouse", "Fast Food", "Juicy chicken roll with creamy sauce.", "149.00", False, "4.5"),
            ("Farmhouse Pizza", "Domino's Pizza", "Pizza", "Loaded pizza with onion, capsicum, tomato, and corn.", "299.00", True, "4.3"),
            ("Chicken Pepperoni Pizza", "Domino's Pizza", "Pizza", "Cheesy pizza topped with chicken pepperoni.", "399.00", False, "4.4"),
            ("Veg Sandwich", "Starbucks", "Fast Food", "Toasted sandwich with fresh vegetables.", "229.00", True, "4.2"),
            ("Strawberry Milk Shake", "Starbucks", "Beverages", "Creamy strawberry shake served chilled.", "249.00", True, "4.3"),
            ("Chocolate Brownie", "Starbucks", "Desserts", "Rich chocolate brownie for dessert lovers.", "199.00", True, "4.2"),
        ]
        created = 0
        for name, restaurant_name, category_name, description, price, is_veg, rating in foods:
            _, was_created = FoodItem.objects.get_or_create(
                name=name,
                restaurant=restaurant_map[restaurant_name],
                defaults={
                    "category": category_map[category_name],
                    "description": description,
                    "price": Decimal(price),
                    "is_veg": is_veg,
                    "is_available": True,
                    "rating": Decimal(rating),
                },
            )
            created += int(was_created)

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin12345"))

        self.stdout.write(self.style.SUCCESS(f"Demo data ready. New food items created: {created}"))
