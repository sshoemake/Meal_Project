from django.db import models
from django.urls import reverse
from app.ingredients.models import Ingredient
from PIL import Image


class Meal(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    notes = models.TextField(null=True, blank=True)
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
    id = models.BigAutoField(primary_key=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["ingredient__aisle"]
