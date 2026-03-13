from django.db.models import F, OuterRef, Subquery
from django.db.models.functions import Floor

from app.ingredients.models import Ing_Store
from app.stores.models import StoreAisleOrder


def get_cart_items_for_store(cart, store):

    cart_items = cart.cart_details.select_related("ingredient")

    ing_store_aisles = (
        Ing_Store.objects.filter(
            store=store,
            ingredient_id=OuterRef("ingredient__id"),
        )
        .values("aisle")[:1]
    )

    cart_items = cart_items.annotate(
        ing_store_aisle=Subquery(ing_store_aisles),
        base_aisle=Floor(F("ing_store_aisle")),
    )

    if store.walk_mode == store.WALK_CUSTOM:

        custom_walk = StoreAisleOrder.objects.filter(
            store=store,
            aisle=OuterRef("base_aisle"),
        ).values("walk_order")[:1]

        cart_items = cart_items.annotate(
            walk_order=Subquery(custom_walk)
        ).order_by("walk_order")

    elif store.walk_mode == store.WALK_REVERSE:

        cart_items = cart_items.order_by("-ing_store_aisle")

    else:

        cart_items = cart_items.order_by("ing_store_aisle")

    return cart_items