from django.urls import path
from .views import cart_list, update_ing_cart, update_meal_cart, select_cart
from . import views

urlpatterns = [
    path("cart/", views.cart_list, name="cart-list"),
    path("cart-ing/<int:pk>/", views.update_ing_cart, name="update-ing-cart"),
    path("cart-meal/<int:pk>/", views.update_meal_cart, name="update-meal-cart"),
    path("cart-select/<int:pk>/", views.select_cart, name="select-cart"),
    path("remove-ing/<int:pk>/", views.remove_ing_cart, name="remove-ing-cart"),
    path("found-ing/<int:pk>/", views.found_ing_cart, name="found-ing-cart"),
]
