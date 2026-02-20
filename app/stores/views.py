from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
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

    def form_valid(self, form):
        # check if default checkbox is checked
        # if so clear all store defaults before updating
        if form.instance.default:
            Store.objects.update(default=False)

        return super().form_valid(form)


class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    success_url = reverse_lazy("store-list")
