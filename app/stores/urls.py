from django.urls import path
from .views import (
    StoreListView,
    StoreCreateView,
    StoreDetailView,
    StoreUpdateView,
    StoreDeleteView,
)
from . import views

urlpatterns = [
    path("store/", StoreListView.as_view(), name="store-list"),
    path("store/new/", StoreCreateView.as_view(), name="store-create"),
    path("store/<int:pk>/", StoreDetailView.as_view(), name="store-detail"),
    path("store/<int:pk>/update/", StoreUpdateView.as_view(), name="store-update"),
    path("store/<int:pk>/delete/", StoreDeleteView.as_view(), name="store-delete"),
]

