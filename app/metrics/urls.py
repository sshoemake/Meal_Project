from django.urls import path

from .views import (
    MetricsListView,
)

urlpatterns = [
    path("metrics/", MetricsListView.as_view(), name="metrics-home"),
]
