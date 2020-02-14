from django.db import models
from django.urls import reverse
from PIL import Image


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True)
    aisle = models.DecimalField(max_digits=4, decimal_places=1)
    auto_add = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["aisle"]

    def get_absolute_url(self):
        return reverse("ingredients-detail", kwargs={"pk": self.pk})


class Meal(models.Model):
    name = models.CharField(max_length=50, unique=True)
    notes = models.TextField()
    image = models.ImageField(default="default.jpg", upload_to="meal_pics")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("meal-detail", kwargs={"pk": self.pk})

    def save(self):
        super().save()

        img = Image.open(self.image)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image)


class Meal_Details(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["ingredient__aisle"]
