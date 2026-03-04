from django.contrib import admin
from .models import Store, StoreAisleOrder


class StoreAisleOrderInline(admin.TabularInline):
    model = StoreAisleOrder
    extra = 0
    ordering = ("walk_order",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "walk_mode")

    def get_inline_instances(self, request, obj=None):
        if obj and obj.walk_mode == Store.WALK_CUSTOM:
            return [StoreAisleOrderInline(self.model, self.admin_site)]
        return []