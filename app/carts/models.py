from django.db import models
from django.db.models import Sum
from app.meals.models import Meal
from app.ingredients.models import Ingredient
from app.users.models import Profile
import datetime


class Cart(models.Model):
    id = models.BigAutoField(primary_key=True)
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

    @classmethod
    def get_or_create_for_user(cls, profile, request=None, yearweek=None):
        """Return a cart for the given profile/yearweek, creating it if needed."""
        if yearweek is None:
            yearweek = current_yearweek()  # helper to get current year+week

        cart, created = cls.objects.get_or_create(profile=profile, yearweek=yearweek)

        if request and created:
            request.session["cart_id"] = cart.id

        return cart

    @property
    def items_total(self):
        # Count all ingredients
        ing_cnt = Cart_Details.objects.filter(cart=self).aggregate(
            total=Sum("quantity")
        )["total"] or 0

        # Count all meals assigned to slots
        slot_cnt = self.meal_slots.count()
        # slot_cnt = self.meal_slots.filter(meal__isnull=False).count()

        return int(ing_cnt) + slot_cnt


class Cart_Details(models.Model):
    id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_details"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    found = models.BooleanField(default=False)


class MealSlot(models.Model):

    class SlotType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        GENERIC = "generic", "Generic"

    class WeekDay(models.IntegerChoices):
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"
        SUNDAY = 7, "Sunday"

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="meal_slots"
    )
    weekday = models.PositiveSmallIntegerField(
        choices=WeekDay.choices,
        null=True,
        blank=True
    )

    slot_type = models.CharField(
        max_length=20,
        choices=SlotType.choices,
        default=SlotType.DINNER
    )

    label = models.CharField(
        max_length=50,
        blank=True
    )  # optional custom name like "Weekly Lunch"

    meal = models.ForeignKey(
        Meal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )