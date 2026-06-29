from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:food_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:food_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('history/', views.order_history, name='order_history'),
]
