from django.shortcuts import render
from django.db.models import Count
from carts.models import Cart
from django.views.generic import (
    ListView,
)


def home(request):
    #context = {"meals": Meal.objects.all()}
    return render(request, "metrics/home.html")


class MetricsListView(ListView):
    template_name = "metrics/home.html"

    def get_queryset(self):
        queryset = Cart.objects.all().values(
            'meals__name').annotate(total=Count('meals')).order_by('-total')[:10]
        return queryset
