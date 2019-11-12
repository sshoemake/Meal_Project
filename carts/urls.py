from django.urls import path
from .views import CartListView, update_ing_cart, update_meal_cart
from . import views

urlpatterns = [
    path("cart/", views.CartListView, name="cart"),
    path("cart-ing/<int:pk>/", views.update_ing_cart, name="update-ing-cart"),
    path("cart-meal/<int:pk>/", views.update_meal_cart, name="update-meal-cart"),
]
