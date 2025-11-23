from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import Store

# Create your views here.


class StoreListView(ListView):
    model = Store
    # ordering = ["name"]
    template_name = "stores/store_list.html"
    context_object_name = "stores"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context.update(cart_header_lists(self.request))
        return context


class StoreCreateView(LoginRequiredMixin, CreateView):
    model = Store
    fields = ["name", "address", "city", "state", "zip_code"]
    # success_url = '/'

    def form_valid(self, form):
        # form.instance.author = self.request.user
        return super().form_valid(form)


class StoreDetailView(DetailView):
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #     meal_details = Meal_Details.objects.filter(ingredient=self.object)

        #     meals = []
        #     for meal_detail in meal_details.all():
        #         meals.append(meal_detail.meal)

        #     context["meals"] = meals

        return context


class StoreUpdateView(LoginRequiredMixin, UpdateView):
    model = Store
    fields = ["name", "address", "city", "state", "zip_code", "default"]

    def form_valid(self, form):
        # form.instance.author = self.request.user

        # check if default checkbox is checked
        # if so clear all store defaults before updating
        if form.instance.default:
            Store.objects.update(default=False)

        return super().form_valid(form)


class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    success_url = reverse_lazy("store-list")
