from django.urls import path
from .views import (
    IngListView,
    IngDetailView,
    IngCreateView,
    IngUpdateView,
    IngDeleteView,
)
from . import views

urlpatterns = [
    path("ingredients/", IngListView.as_view(), name="ingredients-home"),
    path("ingredients/<int:pk>/", IngDetailView.as_view(),
         name="ingredients-detail"),
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
