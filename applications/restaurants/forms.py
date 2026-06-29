from django import forms
from .models import Restaurant, Category, FoodItem


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'name',
            'logo',
            'cover_image',
            'description',
            'cuisine_type',
            'address',
            'rating',
            'delivery_time',
            'is_open',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Restaurant name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a short description about the restaurant'
            }),
            'cuisine_type': forms.TextInput(attrs={
                'placeholder': 'e.g. Biryani, Chinese, Pizza'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter full restaurant address'
            }),
            'rating': forms.NumberInput(attrs={
                'min': '0',
                'max': '5',
                'step': '0.1'
            }),
            'delivery_time': forms.NumberInput(attrs={
                'min': '1',
                'placeholder': 'Delivery time (minutes)'
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name',
            'image',
            'description',
            'is_active',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Pizza, Biryani, Desserts'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Short category description'
            }),
        }


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = [
            'restaurant',
            'category',
            'name',
            'image',
            'description',
            'price',
            'is_veg',
            'is_available',
            'rating',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Food name'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a short description'
            }),
            'price': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01',
                'placeholder': 'Price'
            }),
            'rating': forms.NumberInput(attrs={
                'min': '0',
                'max': '5',
                'step': '0.1'
            }),
        }
