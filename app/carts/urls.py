from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_list, name="cart-list"),
    path(
        "cart/meal/remove/<int:pk>/",
        views.remove_meal_from_cart_view,
        name="meal-remove-from-cart",
    ),
    path("cart-ing/<int:pk>/", views.update_ing_cart, name="update-ing-cart"),
    path("cart-select/<int:pk>/", views.select_cart, name="select-cart"),
    path(
        "cart/ingredient/remove/<int:pk>/",
        views.remove_ing_cart,
        name="cart-ingredient-remove",
    ),
    path("found-ing/<int:pk>/", views.found_ing_cart, name="found-ing-cart"),
]
