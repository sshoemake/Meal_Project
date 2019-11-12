from django.shortcuts import render, redirect
from .models import Cart
from django.views.generic import DetailView
from meals.models import Ingredient, Meal


def CartListView(request):
    final_list = False

    if "final_list" in request.POST:
        # print("final_list")
        # current_final_value = request.POST.get("final_list")
        # print(current_final_value)
        final_list = True

    # print("final_list" in request.POST)
    try:
        the_id = request.session["cart_id"]
    except:
        the_id = None

    if the_id:
        if final_list:
            tmp_cart = Cart.objects.get(id=the_id)
            cart_list = []

            for ingredient in tmp_cart.ingredients.all():
                cart_list.append(ingredient)

            for meal in tmp_cart.meals.all():
                for ingredient in meal.details.all():
                    cart_list.append(ingredient)

            # sort by aisle
            cart_list = sorted(cart_list, key=lambda x: x.aisle)

            context = {"final_list": final_list, "cart_list": cart_list}
        else:
            cart = Cart.objects.get(id=the_id)
            context = {"cart": cart, "final_list": final_list}

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

    if not ingredient in cart.ingredients.all():
        cart.ingredients.add(ingredient)
    else:
        cart.ingredients.remove(ingredient)

    request.session["items_total"] = cart.ingredients.count() + cart.meals.count()

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

    request.session["items_total"] = cart.ingredients.count() + cart.meals.count()

    return redirect("meals-home")
