from django.urls import path
from .views import (
    MealListView,
    MealDetailView,
    MealCreateView,
    MealUpdateView,
    MealDeleteView,
    MealAddCartView,
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
]
