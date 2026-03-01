from app.stores.models import Store
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


def store_renderer(request):
    store_id = request.session.get("def_store")

    # If a store is already set and user selected a new one
    if store_id and "stores" in request.GET:
        new_store_id = request.GET.get("stores")
        if new_store_id:
            request.session["def_store"] = int(new_store_id)

    # If no store in session, determine default
    if not request.session.get("def_store"):
        store = None

        if request.user.is_authenticated:
            try:
                store = request.user.profile.def_store
            except ObjectDoesNotExist:
                store = None

        if not store:
            store = Store.objects.filter(default=True).first()

        request.session["def_store"] = store.id if store else None

    return {
        "all_stores": Store.objects.all(),
    }


def user_theme(request):
    theme = 'light'

    if request.user.is_authenticated:
        pref = request.user.profile.theme

        if pref == 'auto':
            hour = datetime.now().hour
            theme = 'dark' if hour >= 18 or hour < 7 else 'light'
        else:
            theme = pref

    return {
        'theme': f'{theme}'
    }
