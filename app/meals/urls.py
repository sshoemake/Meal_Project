from django.urls import path

from . import views
from .views import (
    MealAddCartView,
    MealCreateView,
    MealDeleteView,
    MealDetailView,
    MealListView,
    MealUpdateView,
)

urlpatterns = [
    path("", MealListView.as_view(), name="meals-home"),
    path("meal/<int:pk>/", MealDetailView.as_view(), name="meal-detail"),
    path("meal/new/", MealCreateView.as_view(), name="meal-create"),
    path("meal/<int:pk>/update/", MealUpdateView.as_view(), name="meal-update"),
    path("addtocart/<int:pk>/", MealAddCartView.as_view(), name="meal-addtocart"),
    path("meal/<int:pk>/delete/", MealDeleteView.as_view(), name="meal-delete"),
    path("about/", views.about, name="meals-about"),
]
