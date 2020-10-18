from django.urls import path
from .views import (
    MealListView,
    MealDetailView,
    MealCreateView,
    MealUpdateView,
    MealDeleteView,
    MealAddCartView,
    IngListView,
    IngDetailView,
    IngCreateView,
    IngUpdateView,
    IngDeleteView,
)
from . import views

urlpatterns = [
    path("", MealListView.as_view(), name="meals-home"),
    path("meal/<int:pk>/", MealDetailView.as_view(), name="meal-detail"),
    path("meal/new2/", MealCreateView.as_view(), name="meal-create"),
    path("meal/new/", views.book_create, name="book_create"),
    path("meal/<int:pk>/update/", MealUpdateView.as_view(), name="meal-update"),
    path("addtocart/<int:pk>/", MealAddCartView.as_view(), name="meal-addtocart"),
    path("meal/<int:pk>/delete/", MealDeleteView.as_view(), name="meal-delete"),
    path("about/", views.about, name="meals-about"),
    path("ingredients/", IngListView.as_view(), name="ingredients-home"),
    path("ingredients/<int:pk>/", IngDetailView.as_view(), name="ingredients-detail"),
    path("ingredients/new/", IngCreateView.as_view(), name="ingredients-create"),
    path(
        "ingredients/<int:pk>/update/",
        IngUpdateView.as_view(),
        name="ingredients-update",
    ),
    path(
        "ingredients/<int:pk>/delete/",
        IngDeleteView.as_view(),
        name="ingredients-delete",
    ),
]
