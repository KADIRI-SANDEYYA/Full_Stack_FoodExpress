from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Restaurant(models.Model):
    name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to="restaurants/logos/")
    cover_image = models.ImageField(upload_to="restaurants/covers/", blank=True, null=True)
    description = models.TextField(blank=True)
    cuisine_type = models.CharField(max_length=100)
    address = models.TextField()
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
            validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    delivery_time = models.PositiveIntegerField(help_text="Delivery time in minutes")
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="foods")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="foods")
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to="foods/", blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
