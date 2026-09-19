from django import forms

from .models import Meal


class BookForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ["name", "notes"]
        # exclude = ("",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            classes = f"{existing} form-control".strip()
            field.widget.attrs.update({"class": classes})

