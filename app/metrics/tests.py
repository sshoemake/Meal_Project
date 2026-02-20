from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from unittest.mock import patch

from app.metrics import views
from app.carts.models import Cart
from app.meals.models import Meal
from django.contrib.auth.models import User
from app.users.models import Profile


class MetricsViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="tester", password="pass")
        self.profile = self.user.profile


    def test_home_uses_render_with_correct_template(self):
        request = self.factory.get("/")
        with patch("app.metrics.views.render") as mock_render:
            mock_render.return_value = HttpResponse("ok")
            response = views.home(request)

            mock_render.assert_called_once_with(request, "metrics/home.html")
            self.assertEqual(response.status_code, 200)


    def test_metrics_list_view_get_queryset_counts_meals(self):
        # Create meals
        m1 = Meal.objects.create(name="Meal A")
        m2 = Meal.objects.create(name="Meal B")

        # Create carts and attach meals to produce different counts
        c1 = Cart.objects.create(yearweek=202201, profile=self.profile)
        c1.meals.add(m1)

        c2 = Cart.objects.create(yearweek=202202, profile=self.profile)
        c2.meals.add(m1)

        c3 = Cart.objects.create(yearweek=202203, profile=self.profile)
        c3.meals.add(m2)

        view = views.MetricsListView()
        qs = list(view.get_queryset())

        counts = {item["meals__name"]: item["total"] for item in qs}

        self.assertEqual(counts.get("Meal A"), 2)
        self.assertEqual(counts.get("Meal B"), 1)
