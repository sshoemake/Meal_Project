from stores.models import Store


def store_renderer(request):
    try:
        store_id = request.session["def_store"]
    except:
        store_id = None

    if store_id:
        if "stores" in request.GET:
            #new_store_id = request.GET["stores"]
            new_store_id = request.GET.get("stores", None)
            request.session["def_store"] = int(new_store_id)
    else:
        if request.user.is_authenticated:
            profile = request.user.profile
            store = profile.def_store
            request.session["def_store"] = store.id
        else:
            store = Store.objects.get(default=True)
            request.session["def_store"] = store.id

    return {'all_stores': Store.objects.all(),
            }
