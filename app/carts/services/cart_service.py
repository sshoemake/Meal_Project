import datetime
from django.db.models import F

from app.ingredients.models import Ingredient

from ..views import get_cart_for_request
from ..models import Cart, Cart_Details

from django.shortcuts import get_object_or_404, redirect
from app.meals.models import Meal
from app.carts.models import MealSlot


def add_meal_to_cart(request, pk, weekday=None, slot_type=None):
    """
    Adds a meal's ingredients to the cart and optionally assigns the meal
    to a MealSlot (weekday/slot_type).
    """

    cart = get_cart_for_request(request)
    meal = get_object_or_404(Meal, id=pk)

    # Add meal ingredients
    add_ingredients_to_cart(request)

    # # Optional meal slot assignment
    # if weekday is not None:

    #     slot, created = MealSlot.objects.get_or_create(
    #         cart=cart,
    #         weekday=int(weekday),
    #         slot_type=slot_type or MealSlot.SlotType.DINNER,
    #         defaults={"meal": meal},
    #     )

    #     if not created:
    #         slot.meal = None if slot.meal_id == meal.id else meal
    #         slot.save()

    # request.session["items_total"] = cart.items_total

    # kwargs = {
    #     "cart": cart,
    #     "weekday": weekday,
    # }

    # if slot_type:
    #     kwargs["slot_type"] = slot_type

    # slot, created = MealSlot.objects.get_or_create(
    #     **kwargs,
    #     defaults={"meal": meal},
    # )

    slot_type = slot_type or MealSlot.SlotType.DINNER

    print(slot_type)
    slot, created = MealSlot.objects.get_or_create(
        cart=cart,
        weekday=weekday,
        slot_type=slot_type,
        meal=meal,
        # defaults={"meal": meal},
    )
    
    print(
        f"Cart:{cart.id} weekday:{weekday} slot:{slot_type} meal:{meal.id} created:{created}"
    )
    
    if not created:
        slot.meal = None if slot.meal_id == meal.id else meal
        slot.save()

    request.session["items_total"] = cart.items_total

    return cart


# @login_required
def add_ingredients_to_cart(request):
    cart = get_cart_for_request(request)

    ing_ids = request.POST.getlist("ingtoadd", [])
    ingredients = Ingredient.objects.filter(id__in=ing_ids)

    add_many_ingredients(cart, ingredients)

    request.session["items_total"] = cart.items_total

    return redirect("ingredients-home")


def get_cart(profile, request, selected_week=None):
    yearweek = convert_sw_yw(selected_week if selected_week is not None else 3)

    cart = Cart.get_or_create_for_user(
        profile,
        request=request,
        yearweek=yearweek,
    )

    request.session["cart_id"] = cart.id
    request.session["items_total"] = cart.items_total
    request.session["selected_week"] = selected_week if selected_week else 3

    return cart


def add_ingredient(cart, ingredient):

    cart_item, created = Cart_Details.objects.get_or_create(
        cart=cart,
        ingredient=ingredient,
        defaults={"quantity": 1},
    )

    if not created:
        Cart_Details.objects.filter(pk=cart_item.pk).update(quantity=F("quantity") + 1)


def remove_ingredient(cart, ingredient):

    cart_item = Cart_Details.objects.filter(
        cart=cart,
        ingredient=ingredient,
    ).first()

    if not cart_item:
        return

    if cart_item.quantity > 1:
        Cart_Details.objects.filter(pk=cart_item.pk).update(quantity=F("quantity") - 1)
    else:
        cart_item.delete()


def remove_meal_from_cart(request, pk, weekday=None, slot_type=None):
    """
    Remove a meal from the cart. If weekday/slot_type is provided,
    only remove from that slot; otherwise remove all instances.
    """
    cart = get_cart_for_request(request)
    meal = get_object_or_404(Meal, id=pk)

    # Remove from a specific slot
    if weekday:
        MealSlot.objects.filter(
            cart=cart,
            meal=meal,
            weekday=weekday,
            slot_type=slot_type or MealSlot.SlotType.DINNER,
        ).delete()
    else:
        # Remove from all slots in this cart
        MealSlot.objects.filter(cart=cart, meal=meal).delete()

    # Update session total (optional, if you track items_total)
    request.session["items_total"] = cart.items_total


def add_many_ingredients(cart, ingredients):

    for ingredient in ingredients:
        add_ingredient(cart, ingredient)


def mark_found(cart, ingredient):

    cart_item = Cart_Details.objects.filter(
        cart=cart,
        ingredient=ingredient,
    ).first()

    if cart_item:
        cart_item.found = True
        cart_item.save()


def ingredient_exists(cart, ingredient):

    return Cart_Details.objects.filter(
        cart=cart,
        ingredient=ingredient,
    ).exists()


def convert_sw_yw(selected_week):

    rel_week = ["-3", "-2", "-1", "0", "1", "2", "3", "4"]

    today = datetime.date.today()
    year, week_num, _ = today.isocalendar()

    week_num += int(rel_week[selected_week])

    if week_num > 53:
        week_num -= 52
        year += 1

    if week_num < 1:
        week_num = 52 + week_num
        year -= 1

    return int(f"{year}{week_num}")
