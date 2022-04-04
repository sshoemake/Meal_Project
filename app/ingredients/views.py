from django.http import JsonResponse
from django.db.models.fields import IntegerField
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
from .models import Ing_Store, Ingredient
#from .forms import BookForm
from carts.views import update_meal_cart, add_ings_cart, get_cart, cart_header_lists, ing_exists_cart
from carts.models import Cart, Cart_Details
from stores.models import Store
from users.models import User, Profile
from django.db.models import Max, Case, When, F, query
import datetime
from django.db.models.expressions import OuterRef, Subquery


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class IngListView(ListView):
    #model = Ingredient
    #ordering = ["name"]

    def get_queryset(self):
        queryset = Ingredient.objects.all().order_by('name')
        #user = self.request.user
        #profile = self.request.user.profile
        def_store = Store.objects.get(id=self.request.session["def_store"])

        ing_store_aisles = Ing_Store.objects.filter(
            store=def_store,
            ingredient_id=OuterRef('id')
        )[:1].values('aisle')

        queryset = queryset.annotate(
            ing_store_aisle=Subquery(ing_store_aisles))

        return queryset

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


class IngDetailView(View):
    def get(self, request, *args, **kwargs):
        view = IngredientDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = IngAisleUpdate.as_view()
        return view(request, *args, **kwargs)


class IngredientDisplay(JSONResponseMixin, DetailView):
    model = Ingredient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        meals = Meal.objects.filter(
            meal_details__in=Meal_Details.objects.filter(ingredient=self.object).all())
        context["meals"] = meals

        ing_in_cart = ing_exists_cart(self.request, self.object)
        context["ing_in_cart"] = ing_in_cart

        store_aisles = Store.objects.all()

        ing_store_aisles = Ing_Store.objects.filter(
            ingredient=self.object,
            store_id=OuterRef('id')
        )[:1].values('aisle')

        store_aisles = store_aisles.annotate(
            ing_store_aisle=Subquery(ing_store_aisles))
        context["store_aisles"] = store_aisles

        return context


class AuthorInterestForm(forms.Form):
    message = forms.CharField()
    # ingredients = Ingredient.objects.all()
    # my_MD = Meal_Details.objects.filter(meal=self.object)
    # curr_ing_ids = my_MD.values_list("ingredient_id", flat=True)


class IngAisleUpdate(SingleObjectMixin, FormView):
    template_name = "ingredients/ingredient_detail.html"
    form_class = AuthorInterestForm
    model = Ingredient

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        meals = Meal.objects.filter(
            meal_details__in=Meal_Details.objects.filter(ingredient=self.object).all())
        context["meals"] = meals

        ing_in_cart = ing_exists_cart(self.request, self.object)
        context["ing_in_cart"] = ing_in_cart

        store_aisles = Store.objects.all()

        ing_store_aisles = Ing_Store.objects.filter(
            ingredient=self.object,
            store_id=OuterRef('id')
        )[:1].values('aisle')

        store_aisles = store_aisles.annotate(
            ing_store_aisle=Subquery(ing_store_aisles))
        context["store_aisles"] = store_aisles

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        my_IS = Ing_Store.objects.filter(ingredient=self.object)
        my_IS.delete()

        for aisle, store_id in zip(request.POST.getlist('Aisles'), request.POST.getlist('Store_ids')):
            if aisle != 'None' and aisle != '':
                try:
                    float(aisle)    # ensure aisle is a float datatype
                    IS_1 = Ing_Store(store_id=store_id,
                                     ingredient=self.object, aisle=aisle)
                    IS_1.save()
                except ValueError:
                    messages.warning(request, "Aisle: '" +
                                     aisle + "' is not a number, skipping!")

        if form.is_valid():
            # Update Meal_Details data (i.e. remove existing and add from page)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("ingredients-detail", kwargs={"pk": self.object.pk})


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
