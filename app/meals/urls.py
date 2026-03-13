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
    path("meal/new/", MealCreateView.as_view(), name="meal-create"),
    path("meal/<int:pk>/update/", MealUpdateView.as_view(), name="meal-update"),
    path("addtocart/<int:pk>/", MealAddCartView.as_view(), name="meal-addtocart"),
    path("meal/<int:pk>/delete/", MealDeleteView.as_view(), name="meal-delete"),
    path("about/", views.about, name="meals-about"),
    path("planner/", views.planner, name="planner"),
    path("meal-picker/<int:cart_id>/<int:weekday>/<str:slot_type>/", views.meal_picker, name="meal-picker"),
    path("assign-meal-slot/", views.assign_meal_slot, name="assign-meal-slot"),
]
