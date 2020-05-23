from django.http import JsonResponse
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
from .models import Meal, Ingredient, Meal_Details
from .forms import BookForm
from carts.views import update_meal_cart, add_ings_cart, get_cart, cart_header_lists
from carts.models import Cart, Cart_Details
import datetime


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


def home(request):
    context = {"meals": Meal.objects.all()}
    return render(request, "meals/home.html", context)


class MealListView(ListView):
    model = Meal
    ordering = ["name"]
    template_name = "meals/home.html"
    context_object_name = "meals"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(cart_header_lists(self.request))

        return context


def get_date_label(int_wk):
    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    week_num = week_num + int(int_wk)
    firstdayofweek = datetime.datetime.strptime(
        f"{year}-W{int(week_num )- 1}-1", "%Y-W%W-%w"
    ).date()

    # return firstdayofweek.strftime("%-m/%-d%<br>%a")
    # return firstdayofweek.strftime("%b %-d%<br>%a")

    return firstdayofweek.strftime("%b %-d")


class MealDetailView(View):
    def get(self, request, *args, **kwargs):
        view = MealDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = MealIngUpdate.as_view()
        return view(request, *args, **kwargs)


class MealAddCartView(View):
    def get(self, request, *args, **kwargs):
        view = MealCartDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # view = MealCartUpdate.as_view()
        # return view(request, *args, **kwargs)
        # meal = get_object_or_404(Meal, pk=kwargs.get("pk", ""))
        # add_meal_cart(meal.pk)
        update_meal_cart(request, **kwargs)
        add_ings_cart(request, **kwargs)

        # for ingredient in request.POST.getlist("ingtoadd"):
        #    print(ingredient)

        messages.success(request, "Your item(s) have been added to the Cart!")
        return redirect("meals-home")


class AuthorInterestForm(forms.Form):
    message = forms.CharField()
    # ingredients = Ingredient.objects.all()
    # my_MD = Meal_Details.objects.filter(meal=self.object)
    # curr_ing_ids = my_MD.values_list("ingredient_id", flat=True)


class MealCartDisplay(DetailView):
    model = Meal
    template_name = "meals/addtocart.html"
    # .objects.filter(id=kwargs.get("pk", "")).first()
    # context = {"meal": model}
    # return render(request, "meals/meal_detail.html", context)

    # def render_to_response(self, context, **response_kwargs):
    #    return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        my_MD = Meal_Details.objects.filter(meal=self.object)
        my_ing_ids = my_MD.values_list("ingredient_id", flat=True)

        context["ing_list"] = Ingredient.objects.filter(id__in=my_ing_ids)
        return context


class MealCartUpdate(SingleObjectMixin, FormView):
    model = Meal
    template_name = "meals/addtocart.html"
    form_class = AuthorInterestForm

    # .objects.filter(id=kwargs.get("pk", "")).first()
    # context = {"meal": model}
    # return render(request, "meals/meal_detail.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        my_MD = Meal_Details.objects.filter(meal=self.object)
        my_ing_ids = my_MD.values_list("ingredient_id", flat=True)

        context["ing_list"] = Ingredient.objects.filter(id__in=my_ing_ids)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        # my_MD = Meal_Details.objects.filter(meal=self.object)
        # my_MD.delete()

        # dd_post = request.POST.getlist("dd_ing_list", None)
        # for ing_id in dd_post:
        #     MD_1 = Meal_Details(ingredient_id=ing_id, meal=self.object, quantity="1")
        #     MD_1.save()

        if form.is_valid():
            # Update Meal_Details data (i.e. remove existing and add from page)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return redirect("meals-home")


class MealIngUpdate(SingleObjectMixin, FormView):
    template_name = "meals/meal_detail.html"
    form_class = AuthorInterestForm
    model = Meal
    # .objects.filter(id=kwargs.get("pk", "")).first()
    # context = {"meal": model}
    # return render(request, "meals/meal_detail.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["form"] = AuthorInterestForm()
        context["message"] = forms.CharField()
        context["ingredients"] = Ingredient.objects.all().order_by("name")
        my_MD = Meal_Details.objects.filter(meal=self.object)
        context["curr_ing_ids"] = my_MD.values_list("ingredient_id", flat=True)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        my_MD = Meal_Details.objects.filter(meal=self.object)
        my_MD.delete()

        dd_post = request.POST.getlist("dd_ing_list", None)
        for ing_id in dd_post:
            MD_1 = Meal_Details(ingredient_id=ing_id, meal=self.object, quantity="1")
            MD_1.save()

        if form.is_valid():
            # Update Meal_Details data (i.e. remove existing and add from page)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse("meal-detail", kwargs={"pk": self.object.pk})


class MealDisplay(JSONResponseMixin, DetailView):
    model = Meal
    # .objects.filter(id=kwargs.get("pk", "")).first()
    # context = {"meal": model}
    # return render(request, "meals/meal_detail.html", context)

    # def render_to_response(self, context, **response_kwargs):
    #    return self.render_to_json_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["form"] = AuthorInterestForm()
        context["message"] = forms.CharField()
        context["ingredients"] = Ingredient.objects.all().order_by("name")
        my_MD = Meal_Details.objects.filter(meal=self.object)
        context["curr_ing_ids"] = my_MD.values_list("ingredient_id", flat=True)
        return context


class MealCreateView(LoginRequiredMixin, CreateView):
    model = Meal
    fields = ["name", "notes", "image"]

    def form_valid(self, form):
        # form.instance.author = self.request.user
        return super().form_valid(form)


class MealUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Meal
    fields = ["name", "notes", "image"]

    def form_valid(self, form):
        # form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # meal = self.get_object()
        # if self.request.user == meal.author:
        #    return True
        # return False
        return True


class MealDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meal
    success_url = "/"

    def test_func(self):
        # meal = self.get_object()
        # if self.request.user == meal.author:
        #    return True
        # return False
        return True


def save_book_form(request, form, template_name):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data["form_is_valid"] = True
            books = Meal.objects.all()
            data["html_book_list"] = render_to_string(
                "meals/includes/partial_meal_list.html", {"books": books}
            )
        else:
            data["form_is_valid"] = False
    context = {"form": form}
    print(context)
    data["html_form"] = render_to_string(template_name, context, request=request)
    print(data)
    return JsonResponse(data)


def about(request):
    return render(request, "meals/about.html", {"title": "About"})


def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
    else:
        form = BookForm()
    return save_book_form(request, form, "meals/includes/partial_meal_create.html")


def book_update(request, **kwargs):
    meal = get_object_or_404(Meal, pk=kwargs.get("pk", ""))

    if request.method == "POST":
        form = BookForm(request.POST, instance=meal)
    else:
        form = BookForm(instance=meal)
    # MD_formset = BookFormset(instance=meal, prefix="ingredients")
    # form = MD_formset
    # form = {"instance": meal}
    # print(context)
    return save_book_form(request, form, "meals/includes/partial_meal_update.html")


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

        meal_details = Meal_Details.objects.filter(ingredient=self.object)

        meals = []
        for meal_detail in meal_details.all():
            meals.append(meal_detail.meal)

        context["meals"] = meals

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
