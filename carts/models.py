from django.db import models
from django.db.models import Sum
from meals.models import Ingredient, Meal


class Cart(models.Model):
    meals = models.ManyToManyField(Meal, blank=True)
    yearweek = models.IntegerField(unique=True)

    @property
    def items_total(self):
        ing_cnt = Cart_Details.objects.filter(cart=self).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

        return int(ing_cnt or 0) + self.meals.count()

    # Add item_cnt property


class Cart_Details(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["ingredient__aisle"]
