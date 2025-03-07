from django.db import models
from django.db.models import Sum
from meals.models import Meal
from ingredients.models import Ingredient
from users.models import Profile
import datetime


class Cart(models.Model):
    id = models.BigAutoField(primary_key=True)
    # meals = models.ManyToManyField(Meal, blank=True)
    yearweek = models.IntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('yearweek', 'profile')

    def __str__(self):
        year = str(self.yearweek)[:4]
        week = str(self.yearweek)[4:]

        firstdayofweek = datetime.datetime.strptime(
            f"{year}-W{int(week)- 1}-4", "%Y-W%W-%w"
        ).date()
        # }-4" <- 4 = Thursday, 1 = Monday, etc.

        my_date = datetime.date.today()
        weeks_back = (my_date - firstdayofweek).days / 7

        return "Cart ID: " + str(self.yearweek) + ", Year: " + year + ", Week: " + week + ", Date: " + firstdayofweek.strftime("%b %-d") + ", weeks back: " + str(int(weeks_back))

    @property
    def items_total(self):
        ing_cnt = Cart_Details.objects.filter(cart=self).aggregate(Sum("quantity"))[
            "quantity__sum"
        ]

        meal_cnt = Meals.objects.filter(cart=self).count()

        return int(ing_cnt or 0) + meal_cnt

    # Add item_cnt property

class Days(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    id = models.BigAutoField(primary_key=True)
    day = models.CharField(max_length=1, choices=DAYS_OF_WEEK)

    #create a Meal_Details class
class Meals(models.Model):
    id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    days = models.ManyToManyField(Days)

class Cart_Details(models.Model):
    id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    found = models.BooleanField(default=False)

    # class Meta:
    #     ordering = ["ingredient__aisle"]
