import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions import Floor
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from app.ingredients.models import Ing_Store, Ingredient
from app.meals.models import Meal
from app.stores.models import Store, StoreAisleOrder

from .models import Cart, Cart_Details


def cart_list(request):
    #request.session["hide_found"] = False

    if request.method == "POST":
        # handle checkbox toggles in session
        request.session['hide_found'] = 'hide_found' in request.POST
        # request.session['reverse_sort'] = 'reverse_sort' in request.POST
        # redirect to GET to render full context
        return redirect(reverse('cart-list'))
    
    cart = get_cart(request)
    hide_found = request.session.get('hide_found', False)

    if cart:
        cart_items = Cart_Details.objects.filter(cart=cart)
        # join aisle detail from store linked to user's profile
        #profile = request.user.profile
        def_store = Store.objects.get(id=request.session["def_store"])

        ing_store_aisles = Ing_Store.objects.filter(
            store=def_store,
            ingredient_id=OuterRef('ingredient__id')
        )[:1].values('aisle')

        cart_items = cart_items.annotate(
            ing_store_aisle=Subquery(ing_store_aisles),
            base_aisle=Floor(F("ing_store_aisle"))
        )

        if def_store.walk_mode == Store.WALK_CUSTOM:

            custom_walk = StoreAisleOrder.objects.filter(
                store=def_store,
                aisle=OuterRef('base_aisle')
            ).values('walk_order')[:1]

            cart_items = cart_items.annotate(
                walk_order=Subquery(custom_walk)
            ).order_by('walk_order')

        elif def_store.walk_mode == Store.WALK_REVERSE:

            cart_items = cart_items.order_by('-ing_store_aisle')

        else:

            cart_items = cart_items.order_by('ing_store_aisle')

        # if def_store.walk_mode == Store.WALK_REVERSE:
        #     cart_items = cart_items.order_by('-ing_store_aisle')
        # else:
        #     cart_items = cart_items.order_by('ing_store_aisle')

    empty = (cart.meals.count() == 0 and cart_items.count() == 0)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'hide_found': hide_found,
        'empty': empty,
        'empty_message': "Your shopping cart is empty.",
    }

    # add cart header partial details to context
    context.update(cart_header_lists(request))
    
    return render(request, "carts/cart_list.html", context)


def cart_header_lists(request):
    # calc date_list: current week +-3 weeks
    date_list = []
    for num in range(-3, 4):
        date_list.append(get_date_label(num))

    # Populate the meal list:
    meal_list = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]

    request.session.setdefault("selected_week", 3)

    local_ctx = {}
    local_ctx["date_list"] = date_list
    local_ctx["meal_list"] = meal_list
    return local_ctx


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
        f"{year}-W{int(week_num )- 1}-4", "%Y-W%W-%w"
    ).date()
    # }-4" <- 4 = Thursday, 1 = Monday, etc.
    # return firstdayofweek.strftime("%-m/%-d%<br>%a")
    # return firstdayofweek.strftime("%b %-d%<br>%a")

    return firstdayofweek.strftime("%b %-d")


@login_required
def update_ing_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    ingredient = get_object_or_404(Ingredient, id=kwargs.get("pk"))

    cart_items = Cart_Details.objects.filter(cart=cart)
    my_ing_ids = cart_items.values_list("ingredient_id", flat=True)

    if ingredient.id not in my_ing_ids:
        Cart_Details.objects.create(
            cart=cart,
            ingredient=ingredient,
            quantity=1,
        )
    else:
        Cart_Details.objects.filter(
            cart=cart,
            ingredient=ingredient,
        ).update(quantity=F("quantity") + 1)

    request.session["items_total"] = cart.items_total

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def update_meal_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    meal = get_object_or_404(Meal, id=kwargs.get("pk"))

    if cart.meals.filter(id=meal.id).exists():
        cart.meals.remove(meal)
    else:
        cart.meals.add(meal)

    request.session["items_total"] = cart.items_total

    return redirect("meals-home")


def select_cart(request, **kwargs):
    request.session["selected_week"] = kwargs.get("pk", "")

    # Update the Cart_id
    request.session["cart_id"] = chg_cart_or_create(request)
    cart = get_cart(request)
    request.session["items_total"] = cart.items_total

    # return redirect("meals-home")
    # return to source/original url!
    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def remove_ing_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    ingredient = Ingredient.objects.filter(pk=kwargs.get("pk")).first()
    if not ingredient:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    cart_item = Cart_Details.objects.filter(
        cart=cart,
        ingredient=ingredient
    ).first()

    if not cart_item:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if cart_item.quantity > 1:
        cart_item.quantity = F("quantity") - 1
        cart_item.save()
    else:
        cart_item.delete()

    request.session["items_total"] = cart.items_total

    return redirect(request.META.get("HTTP_REFERER", "/"))


def found_ing_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    try:
        ingredient = Ingredient.objects.get(pk=kwargs.get("pk"))
    except Ingredient.DoesNotExist:
        return HttpResponse("OK")  # graceful exit

    cart_item = Cart_Details.objects.filter(
        cart=cart,
        ingredient=ingredient
    ).first()

    if cart_item:
        cart_item.found = True
        cart_item.save()

    return HttpResponse("OK")


@login_required
def add_ings_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    ing_ids = request.POST.getlist("ingtoadd", [])

    # Fetch all ingredients in one query
    ingredients = Ingredient.objects.filter(id__in=ing_ids)

    for ingredient in ingredients:
        cart_detail, created = Cart_Details.objects.get_or_create(
            cart=cart,
            ingredient=ingredient,
            defaults={"quantity": 1},
        )

        if not created:
            cart_detail.quantity = F("quantity") + 1
            cart_detail.save()

    request.session["items_total"] = cart.items_total

    return redirect("ingredients-home")


def ing_exists_cart(request, ing):
    cart = get_cart(request)

    found = False
    if cart:
        cart_items = Cart_Details.objects.filter(cart=cart)
        my_ing_ids = cart_items.values_list("ingredient_id", flat=True)

        if ing.id in my_ing_ids:
            found = True

    return found



def get_cart(request):
    cart_id = request.session.get("cart_id")

    if not cart_id:
        return None

    return Cart.objects.filter(id=cart_id).first()


def get_cart_or_create(request):
    cart = get_cart(request)

    if cart:
        return cart

    cart = Cart.objects.create()
    request.session["cart_id"] = cart.id
    return cart


def chg_cart_or_create(request):
    selected_week = request.session.get("selected_week")

    if not selected_week:
        return None  # or raise a controlled error

    yearweek = convert_sw_yw(selected_week)

    profile = getattr(request.user, "profile", None)
    if not profile:
        return None  # or raise

    cart, _ = Cart.objects.get_or_create(
        yearweek=yearweek,
        profile=profile,
    )

    return cart.id


def convert_sw_yw(selected_week):
    # -3|-2|-1|0|1|2|3|4 <-- relative week
    # 0| 1| 2|3|4|5|6|7 <-- selected_week index

    rel_week = ["-3", "-2", "-1", "0", "1", "2", "3", "4"]

    my_date = datetime.date.today()
    year, week_num, day_of_week = my_date.isocalendar()
    week_num = week_num + int(rel_week[selected_week])

    if week_num > 53:
        week_num = week_num - 52
        year = year + 1

    if week_num < 1:
        week_num = 52 + week_num
        year = year - 1

    return int(str(year) + str(week_num))
