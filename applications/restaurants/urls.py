from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('restaurants/', views.restaurant_list, name='restaurants'),
    path('restaurants/<int:restaurant_id>/foods/', views.food_list, name='food_list'),
    path('foods/<int:food_id>/', views.single_food, name='single_food'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/restaurants/add/', views.add_restaurant, name='add_restaurant'),
    path('manager/categories/add/', views.add_category, name='add_category'),
    path('manager/foods/add/', views.add_food, name='add_food'),
]
