from django.shortcuts import render
from django import forms
from django.forms import modelformset_factory
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.loader import render_to_string
from django.views import View
from django.views.generic.edit import FormMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.views.generic.detail import SingleObjectMixin
from meals.models import Meal, Meal_Details
from .models import Ingredient
#from .forms import BookForm
from carts.views import update_meal_cart, add_ings_cart, get_cart, cart_header_lists, ing_exists_cart
from carts.models import Cart, Cart_Details
import datetime


class IngListView(ListView):
    model = Ingredient
    ordering = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = get_cart(self.request)

        if cart:
            cart_details = Cart_Details.objects.filter(cart=cart)
        else:
            cart_details = Cart_Details.objects.none()

        cart_item_list = []
        for cd in cart_details.all():
            cart_item_list.append(cd.ingredient)

        context["cart_item_list"] = cart_item_list
        context.update(cart_header_lists(self.request))

        return context


class IngDetailView(DetailView):
    model = Ingredient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # meal_details = Meal_Details.objects.filter(ingredient=self.object)
        meals = Meal.objects.filter(
            meal_details__in=Meal_Details.objects.filter(ingredient=self.object).all())

        context["meals"] = meals

        ing_in_cart = ing_exists_cart(self.request, self.object)
        context["ing_in_cart"] = ing_in_cart

        return context


class IngCreateView(LoginRequiredMixin, CreateView):
    model = Ingredient
    fields = ["name", "aisle", "auto_add"]
    # success_url = '/'

    def form_valid(self, form):
        # form.instance.author = self.request.user
        return super().form_valid(form)


class IngUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ingredient
    fields = ["name", "aisle", "auto_add"]

    def form_valid(self, form):
        # form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # meal = self.get_object()
        # if self.request.user == meal.author:
        #    return True
        # return False
        return True


class IngDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ingredient
    success_url = reverse_lazy("ingredients-home")

    def test_func(self):
        # meal = self.get_object()
        # if self.request.user == meal.author:
        #    return True
        # return False
        return True
