from django.db import models
from meals.models import Ingredient, Meal


class Cart(models.Model):
    ingredients = models.ManyToManyField(Ingredient, null=True, blank=True)
    meals = models.ManyToManyField(Meal, null=True, blank=True)

    class Meta:
        ordering = ["ingredients__aisle"]
