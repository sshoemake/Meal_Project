from django import forms

from .models import Meal, Ingredient, Meal_Details


class BookForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ["name", "notes"]
        # exclude = ("",)


# BookFormset = forms.inlineformset_factory(Meal, Meal_Details, form=BookForm, extra=2)

# Representing the many to many related field in Pizza
# ingredients = forms.ModelMultipleChoiceField(queryset=Ingredient.objects.all())

# Overriding __init__ here allows us to provide initial
# data for 'toppings' field
# def __init__(self, *args, **kwargs):
#     super(BookForm, self).__init__(*args, **kwargs)
#     self.fields["ingredients"].queryset = Ingredient.objects.all()

# Only in case we build the form from an instance
# (otherwise, 'toppings' list should be empty)
# if kwargs.get("instance"):
# We get the 'initial' keyword argument or initialize it
# as a dict if it didn't exist.
# initial = kwargs.setdefault("initial", {})
# The widget for a ModelMultipleChoiceField expects
# a list of primary key for the selected data.
# initial["ingredients"] = [
# t.pk for t in kwargs["instance"].meal_details_set.all()
# ]

#    forms.ModelForm.__init__(self, *args, **kwargs)
