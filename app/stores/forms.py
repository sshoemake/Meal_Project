from django.forms import inlineformset_factory
from .models import Store, StoreAisleOrder

StoreAisleOrderFormSet = inlineformset_factory(
    Store,
    StoreAisleOrder,
    fields=("aisle", "walk_order"),
    extra=3,   # allow adding new rows
    can_delete=True
)