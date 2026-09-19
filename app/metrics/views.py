from django.db.models import Count
from django.shortcuts import render
from django.views.generic import (
    ListView,
)

from app.carts.models import Cart


def home(request):
    return render(request, "metrics/home.html")


class MetricsListView(ListView):
    template_name = "metrics/home.html"

    def get_queryset(self):
        queryset = Cart.objects.all().values(
            'meals__name').annotate(total=Count('meals')).order_by('-total')[:10]
        return queryset
