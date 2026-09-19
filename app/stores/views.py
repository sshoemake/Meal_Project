from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from app.stores.forms import StoreAisleOrderFormSet

from .models import Store


class StoreListView(ListView):
    model = Store

    template_name = "stores/store_list.html"
    context_object_name = "stores"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class StoreCreateView(LoginRequiredMixin, CreateView):
    model = Store
    fields = ["name", "address", "city", "state", "zip_code", "walk_mode"]

    def form_valid(self, form):
        return super().form_valid(form)


class StoreDetailView(DetailView):
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class StoreUpdateView(LoginRequiredMixin, UpdateView):
    model = Store
    fields = ["name", "address", "city", "state", "zip_code", "default", "walk_mode"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = StoreAisleOrderFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context["formset"] = StoreAisleOrderFormSet(
                instance=self.object
            )

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if form.instance.default:
            Store.objects.update(default=False)
        # Only validate/save the formset if management form data was submitted.
        post_has_management = any(k.endswith("-TOTAL_FORMS") for k in self.request.POST.keys())

        if post_has_management:
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
                return super().form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            # No formset submitted; just save the main form.
            self.object = form.save()
            return super().form_valid(form)
        

class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    success_url = reverse_lazy("store-list")
