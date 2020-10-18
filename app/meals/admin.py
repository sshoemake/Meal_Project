from django.contrib import admin
from .models import Meal, Ingredient, Meal_Details

admin.site.register(Meal)
admin.site.register(Ingredient)
admin.site.register(Meal_Details)
