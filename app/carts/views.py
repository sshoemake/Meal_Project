from django.shortcuts import render, redirect
from .models import Cart, Cart_Details
from django.views.generic import DetailView
from meals.models import Ingredient, Meal
from django.db.models import F, Sum
from django.http import HttpResponse
import datetime


def CartListView(request):
    #request.session["hide_found"] = False

    if request.method == "POST":
        if "hide_found" in request.POST:
            request.session["hide_found"] = True
        else:
            request.session["hide_found"] = False

    cart = get_cart(request)

    if cart:
        cart_items = Cart_Details.objects.filter(cart=cart)

        context = {"cart": cart, "cart_items": cart_items}
    else:
        empty_message = "Your Cart is Empty, please keep shopping."
        context = {"empty": True, "empty_message": empty_message}

    # add cart header partial details to context
    context.update(cart_header_lists(request))

    template = "carts/cart_list.html"
    return render(request, template, context)


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


def update_ing_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    try:
        ingredient = Ingredient.objects.filter(id=kwargs.get("pk", "")).first()
    except Ingredient.DoesNotExist:
        pass
    except:
        pass

    cart_items = Cart_Details.objects.filter(cart=cart)
    my_ing_ids = cart_items.values_list("ingredient_id", flat=True)

    if not ingredient.id in my_ing_ids:
        add_CD = Cart_Details(cart=cart, ingredient=ingredient, quantity="1")
        add_CD.save()
    else:
        update_CD = Cart_Details.objects.get(cart=cart, ingredient=ingredient)
        update_CD.quantity = F("quantity") + 1
        update_CD.save()

    request.session["items_total"] = cart.items_total

    # return redirect("ingredients-home")
    return redirect(request.META.get("HTTP_REFERER", "/"))


def update_meal_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    try:
        meal = Meal.objects.filter(id=kwargs.get("pk", "")).first()
    except Meal.DoesNotExist:
        pass
    except:
        pass

    if not meal in cart.meals.all():
        cart.meals.add(meal)
    else:
        cart.meals.remove(meal)

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


def remove_ing_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    try:
        ingredient = Ingredient.objects.filter(id=kwargs.get("pk", "")).first()
    except Ingredient.DoesNotExist:
        pass
    except:
        pass

    cart_items = Cart_Details.objects.filter(cart=cart)
    my_ing_ids = cart_items.values_list("ingredient_id", flat=True)

    if ingredient.id in my_ing_ids:
        update_CD = Cart_Details.objects.get(cart=cart, ingredient=ingredient)
        if update_CD.quantity > 1:
            update_CD.quantity = F("quantity") - 1
            update_CD.save()
        else:
            update_CD.delete()

    request.session["items_total"] = cart.items_total

    # return redirect("ingredients-home")
    return redirect(request.META.get("HTTP_REFERER", "/"))


def found_ing_cart(request, **kwargs):
    #hide_found = False

    # if "hide_found" in request.GET:
    # print("final_list")
    # current_final_value = request.POST.get("final_list")
    # print(current_final_value)
    #    hide_found = True

    cart = get_cart_or_create(request)

    try:
        ingredient = Ingredient.objects.filter(id=kwargs.get("pk", "")).first()
    except Ingredient.DoesNotExist:
        pass
    except:
        pass

    cart_items = Cart_Details.objects.filter(cart=cart)
    my_ing_ids = cart_items.values_list("ingredient_id", flat=True)

    if ingredient.id in my_ing_ids:
        update_CD = Cart_Details.objects.get(cart=cart, ingredient=ingredient)
        update_CD.found = True
        update_CD.save()

    return HttpResponse("OK")
    # return redirect("ingredients-home")
    # return redirect(request.META.get("HTTP_REFERER", "/"))


def add_ings_cart(request, **kwargs):
    cart = get_cart_or_create(request)

    cart_items = Cart_Details.objects.filter(cart=cart)
    my_ing_ids = cart_items.values_list("ingredient_id", flat=True)

    try:
        ing_ids = request.POST.getlist("ingtoadd")
    # except Ingredient.DoesNotExist:
    #    pass
    except:
        pass

    for ing_id in ing_ids:
        ingredient = Ingredient.objects.get(id=ing_id)
        if not ingredient.id in my_ing_ids:
            add_CD = Cart_Details(
                cart=cart, ingredient=ingredient, quantity="1")
            add_CD.save()
        else:
            update_CD = Cart_Details.objects.get(
                cart=cart, ingredient=ingredient)
            update_CD.quantity = F("quantity") + 1
            update_CD.save()

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
    try:
        the_id = request.session["cart_id"]
    except:
        the_id = None

    if the_id:
        return Cart.objects.get(id=the_id)
    else:
        return None


def get_cart_or_create(request):
    try:
        the_id = request.session["cart_id"]
    except:
        new_cart = Cart()
        new_cart.save()
        request.session["cart_id"] = new_cart.id
        the_id = new_cart.id

    return Cart.objects.get(id=the_id)


def chg_cart_or_create(request):
    selected_week = request.session["selected_week"]
    yearweek = convert_sw_yw(selected_week)

    try:
        existing_cart = Cart.objects.get(yearweek=yearweek)
        the_id = existing_cart.id
    except:
        new_cart = Cart()
        new_cart.yearweek = yearweek
        new_cart.save()
        the_id = new_cart.id

    return the_id


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
