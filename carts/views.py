from django.shortcuts import render, redirect
from .models import Cart, Cart_Details
from django.views.generic import DetailView
from meals.models import Ingredient, Meal
from django.db.models import F


def CartListView(request):
    try:
        the_id = request.session["cart_id"]
    except:
        the_id = None

    if the_id:
        cart = Cart.objects.get(id=the_id)
        cart_items = Cart_Details.objects.filter(cart=cart)
        # cart = cart.objects.order_by("ingredients__aisle")
        context = {"cart": cart, "cart_items": cart_items}

    else:
        empty_message = "Your Cart is Empty, please keep shopping."
        context = {"empty": True, "empty_message": empty_message}

    # cart = Cart.objects.all()[0]
    # context = {"cart": cart}
    template = "carts/cart_list.html"
    return render(request, template, context)


def update_ing_cart(request, **kwargs):
    try:
        the_id = request.session["cart_id"]
    except:
        new_cart = Cart()
        new_cart.save()
        request.session["cart_id"] = new_cart.id
        the_id = new_cart.id

    cart = Cart.objects.get(id=the_id)

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

    ## TODO fix the cart count, missing ingredient count
    request.session["items_total"] = (
        Cart_Details.objects.filter(cart=cart).count() + cart.meals.count()
    )

    return redirect("ingredients-home")


def update_meal_cart(request, **kwargs):
    try:
        the_id = request.session["cart_id"]
    except:
        new_cart = Cart()
        new_cart.save()
        request.session["cart_id"] = new_cart.id
        the_id = new_cart.id

    cart = Cart.objects.get(id=the_id)

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

    ## TODO ##
    ## add back the ingredient count cart.ingredients.count() +
    request.session["items_total"] = (
        Cart_Details.objects.filter(cart=cart).count() + cart.meals.count()
    )

    return redirect("meals-home")


def remove_ing_cart(request, **kwargs):
    try:
        the_id = request.session["cart_id"]
    except:
        new_cart = Cart()
        new_cart.save()
        request.session["cart_id"] = new_cart.id
        the_id = new_cart.id

    cart = Cart.objects.get(id=the_id)

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

    ## TODO fix the cart count, missing ingredient count
    request.session["items_total"] = (
        Cart_Details.objects.filter(cart=cart).count() + cart.meals.count()
    )

    return redirect("ingredients-home")


def add_ings_cart(request, **kwargs):
    try:
        the_id = request.session["cart_id"]
    except:
        new_cart = Cart()
        new_cart.save()
        request.session["cart_id"] = new_cart.id
        the_id = new_cart.id

    cart = Cart.objects.get(id=the_id)
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
            add_CD = Cart_Details(cart=cart, ingredient=ingredient, quantity="1")
            add_CD.save()
        else:
            update_CD = Cart_Details.objects.get(cart=cart, ingredient=ingredient)
            update_CD.quantity = F("quantity") + 1
            update_CD.save()

    ## TODO ##
    ## cart.ingredients.count() +
    request.session["items_total"] = (
        Cart_Details.objects.filter(cart=cart).count() + cart.meals.count()
    )

    return redirect("ingredients-home")
