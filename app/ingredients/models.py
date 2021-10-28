from django.db import models
from django.urls import reverse


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
