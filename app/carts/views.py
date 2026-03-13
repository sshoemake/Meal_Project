import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .selectors import cart_selectors
from .services import cart_service

from app.ingredients.models import Ingredient
from app.stores.models import Store


def redirect_back(request, default="/"):
    return redirect(request.META.get("HTTP_REFERER", default))


def cart_list(request):

    if request.method == "POST":
        request.session["hide_found"] = "hide_found" in request.POST
        return redirect(reverse("cart-list"))

    store = get_object_or_404(Store, id=request.session["def_store"])
    cart = get_cart_for_request(request)
    cart_items = cart_selectors.get_cart_items_for_store(cart, store)
    meals = cart.meal_slots.select_related("meal").distinct()

    hide_found = request.session.get("hide_found", False)
    empty = cart.meal_slots.count() == 0 and cart_items.count() == 0

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "cart_meals": meals,
        "hide_found": hide_found,
        "empty": empty,
        "empty_message": "Your shopping cart is empty",
    }

    context.update(cart_header_lists(request))

    return render(request, "carts/cart_list.html", context)


def cart_header_lists(request):

    date_list = [get_date_label(num) for num in range(-3, 4)]

    meal_list = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]

    request.session.setdefault("selected_week", 3)

    return {
        "date_list": date_list,
        "meal_list": meal_list,
    }


def get_date_label(offset):

    today = datetime.date.today()
    year, week_num, _ = today.isocalendar()

    week_num += int(offset)

    if week_num > 53:
        week_num -= 52
        year += 1

    if week_num < 1:
        week_num = 52 + week_num
        year -= 1

    first_day = datetime.datetime.strptime(
        f"{year}-W{int(week_num)-1}-4",
        "%Y-W%W-%w",
    ).date()

    return first_day.strftime("%b %-d")


@login_required
def update_ing_cart(request, pk):

    cart = get_cart_for_request(request)

    ingredient = get_object_or_404(Ingredient, id=pk)

    cart_service.add_ingredient(cart, ingredient)

    request.session["items_total"] = cart.items_total

    return redirect_back(request)


@login_required
def remove_ing_cart(request, pk):

    cart = get_cart_for_request(request)

    ingredient = get_object_or_404(Ingredient, id=pk)

    cart_service.remove_ingredient(cart, ingredient)

    request.session["items_total"] = cart.items_total

    return redirect_back(request)


# @login_required
# def update_meal_cart(request, pk, weekday=None, slot_type=None):

#     cart = get_cart_for_request(request)
#     meal = get_object_or_404(Meal, id=pk)

#     weekday = weekday or request.POST.get("weekday")
#     slot_type = slot_type or request.POST.get("slot_type")

#     # slot, created = MealSlot.objects.get_or_create(
#     #     cart=cart,
#     #     weekday=weekday,
#     #     slot_type=slot_type,
#     #     defaults={"meal": meal},
#     # )

#     # if not created:
#     #     # toggle behavior
#     #     slot.meal = None if slot.meal_id == meal.id else meal
#     #     slot.save()

#     kwargs = {
#         "cart": cart,
#         "weekday": weekday,
#     }

#     if slot_type:
#         kwargs["slot_type"] = slot_type

#     slot, created = MealSlot.objects.get_or_create(
#         **kwargs,
#         defaults={"meal": meal},
#     )

#     if not created:
#         slot.meal = None if slot.meal_id == meal.id else meal
#         slot.save()

#     request.session["items_total"] = cart.items_total


@login_required
def remove_meal_from_cart_view(request, pk):

    if request.method == "POST":
        weekday = request.POST.get("weekday")
        slot_type = request.POST.get("slot_type")

        cart_service.remove_meal_from_cart(
            request,
            pk=pk,
            weekday=weekday,
            slot_type=slot_type,
        )

        messages.success(request, "Meal removed from your cart.")

    return redirect("meals-home")


@login_required
def select_cart(request, pk=None):

    get_cart_for_request(request, selected_week=pk)

    return redirect_back(request)


def found_ing_cart(request, pk):

    cart = get_cart_for_request(request)
    ingredient = get_object_or_404(Ingredient, id=pk)

    cart_service.mark_found(cart, ingredient)

    return HttpResponse("OK")


def ing_exists_cart(request, ing):

    cart = get_cart_for_request(request)

    return cart_service.ingredient_exists(cart, ing)


def get_cart_for_request(request, selected_week=None):

    profile = getattr(request.user, "profile", None)

    if not profile:
        raise ValueError("User has no profile")

    if selected_week is None:
        selected_week = request.session.get("selected_week", 3)

    return cart_service.get_cart(profile, request, selected_week)
