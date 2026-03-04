from django.db import models
from django.urls import reverse


class Store(models.Model):
    WALK_STANDARD = "standard"
    WALK_REVERSE = "reverse"
    WALK_CUSTOM = "custom"

    WALK_CHOICES = [
        (WALK_STANDARD, "Standard (1 → N)"),
        (WALK_REVERSE, "Reverse (N → 1)"),
        (WALK_CUSTOM, "Custom Layout"),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=100, blank=True)

    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    default = models.BooleanField(default=False)
    walk_mode = models.CharField(
        max_length=10,
        choices=WALK_CHOICES,
        default=WALK_STANDARD,
    )
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("store-detail", kwargs={"pk": self.pk})

class StoreAisleOrder(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="aisle_orders")
    aisle = models.DecimalField(max_digits=4, decimal_places=1)
    walk_order = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ("store", "aisle"),
            ("store", "walk_order"),
        )
        indexes = [
            models.Index(fields=["store", "walk_order"]),
        ]
        ordering = ["walk_order"]