from django.urls import path
from .views import (
    MetricsListView,
)
from . import views

urlpatterns = [
    path("metrics/", MetricsListView.as_view(), name="metrics-home"),
]
