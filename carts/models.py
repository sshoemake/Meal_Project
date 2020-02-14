from django.db import models
from meals.models import Ingredient, Meal


class Cart(models.Model):
    meals = models.ManyToManyField(Meal, null=True, blank=True)

    class Meta:
        ordering = ["ingredients__aisle"]


class Cart_Details(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["ingredient__aisle"]
