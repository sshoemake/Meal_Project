from django.http import JsonResponse
from django import forms
# removed unused import: modelformset_factory
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.loader import render_to_string
from django.views import View
# removed unused import: FormMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.views.generic.detail import SingleObjectMixin

from app.carts.services.cart_service import add_meal_to_cart
from .models import Meal, Ingredient, Meal_Details
from .forms import BookForm
from app.carts.views import get_cart_for_request, cart_header_lists
from app.carts.models import Cart, MealSlot
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
    if week_num > 53:
        week_num = week_num - 52
        year = year + 1

    if week_num < 1:
        week_num = 52 + week_num
        year = year - 1

    firstdayofweek = datetime.datetime.strptime(
        f"{year}-W{int(week_num )- 1}-1", "%Y-W%W-%w"
    ).date()

    return firstdayofweek.strftime("%b %-d")


class MealDetailView(View):
    def get(self, request, *args, **kwargs):
        view = MealDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = MealIngUpdate.as_view()
        return view(request, *args, **kwargs)


class MealAddCartView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = MealCartDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, pk):

        weekday = request.POST.get("weekday")
        slot_type = request.POST.get("slot_type")

        add_meal_to_cart(
            request,
            pk=pk,
            weekday=weekday,
            slot_type=slot_type
        )

        messages.success(request, "Your item(s) have been added to the Cart!")

        return redirect("meals-home")


class AuthorInterestForm(forms.Form):
    message = forms.CharField()


class MealCartDisplay(DetailView):
    model = Meal
    template_name = "meals/addtocart.html"

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        my_MD = Meal_Details.objects.filter(meal=self.object)
        my_ing_ids = my_MD.values_list("ingredient_id", flat=True)

        context["ing_list"] = Ingredient.objects.filter(id__in=my_ing_ids)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            # Update Meal_Details data (i.e. remove existing and add from page)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return redirect("meals-home")


class MealIngUpdate(LoginRequiredMixin, SingleObjectMixin, FormView):
    template_name = "meals/meal_detail.html"
    form_class = AuthorInterestForm
    model = Meal

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
            MD_1 = Meal_Details(ingredient_id=ing_id,
                                meal=self.object, quantity="1")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["form"] = AuthorInterestForm()
        context["message"] = forms.CharField()
        context["ingredients"] = Ingredient.objects.all().order_by("name")
        my_MD = Meal_Details.objects.filter(meal=self.object)
        context["curr_ing_ids"] = my_MD.values_list("ingredient_id", flat=True)

        # Find all the carts this meal exists in
        carts = Cart.objects.filter(
            meals__in=[self.object])

        context["carts"] = carts

        return context


class MealCreateView(LoginRequiredMixin, CreateView):
    model = Meal
    fields = ["name", "notes", "image"]

    def form_valid(self, form):
        # Save the object first
        self.object = form.save()
        # If this is an AJAX request, respond with JSON containing
        # the rendered partials expected by the frontend.
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = {"form_is_valid": True}
            data["html_book_list"] = render_to_string(
                "meals/includes/partial_meal_list.html",
                {"books": Meal.objects.all()},
                request=self.request,
            )
            return JsonResponse(data)

        return super().form_valid(form)

    def form_invalid(self, form):
        # Return JSON for AJAX requests so the frontend can update the modal/form
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            context = {"form": form}
            html_form = render_to_string(
                "meals/includes/partial_meal_create.html",
                context,
                request=self.request,
            )
            return JsonResponse({"form_is_valid": False, "html_form": html_form})

        return super().form_invalid(form)


class MealUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Meal
    fields = ["name", "notes", "image"]

    def form_valid(self, form):
        # form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return True


class MealDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meal
    success_url = "/"

    def test_func(self):
        return True


def about(request):
    return render(request, "meals/about.html", {"title": "About"})


# `book_create` and `save_book_form` logic has been consolidated into
# `MealCreateView`. `meal_update` implements the partial-update JSON
# response inline below.

def meal_update(request, **kwargs):
    meal = get_object_or_404(Meal, pk=kwargs.get("pk", ""))

    if request.method == "POST":
        form = BookForm(request.POST, instance=meal)
    else:
        form = BookForm(instance=meal)

    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data["form_is_valid"] = True
            books = Meal.objects.all()
            data["html_book_list"] = render_to_string(
                "meals/includes/partial_meal_list.html", {"books": books}, request=request
            )
        else:
            data["form_is_valid"] = False

    context = {"form": form}
    data["html_form"] = render_to_string(
        "meals/includes/partial_meal_update.html", context, request=request
    )
    return JsonResponse(data)


def planner(request):

    # cart = Cart.objects.get(profile=request.user.profile)
    cart = get_cart_for_request(request)

    weekdays = [
        (1, "Mon"),
        (2, "Tue"),
        (3, "Wed"),
        (4, "Thu"),
        (5, "Fri"),
        (6, "Sat"),
        (7, "Sun"),
    ]

    slot_types = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
    ]

    context = {
        "cart": cart,
        "weekdays": weekdays,
        "slot_types": slot_types,
    }

    return render(request, "meals/planner.html", context)


def meal_picker(request, cart_id, weekday, slot_type):

    meals = Meal.objects.all()

    context = {
        "meals": meals,
        "cart_id": cart_id,
        "weekday": weekday,
        "slot_type": slot_type,
    }

    return render(request, "meals/meal_picker.html", context)


def assign_meal_slot(request):

    # cart = get_object_or_404(Cart, id=request.POST["cart_id"])
    cart = get_cart_for_request(request)

    weekday = int(request.POST["weekday"])
    slot_type = request.POST["slot_type"]
    meal_id = request.POST["meal_id"]

    meal = get_object_or_404(Meal, id=meal_id)

    slot, created = MealSlot.objects.get_or_create(
        cart=cart,
        weekday=weekday,
        slot_type=slot_type
    )

    slot.meal = meal
    slot.save()

    return render(
        request,
        "meals/partials/meal_cell.html",
        {"slot": slot}
    )
