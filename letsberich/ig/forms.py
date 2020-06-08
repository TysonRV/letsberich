from django import forms
from django.forms import SelectDateWidget

from letsberich.ig.models import Position


class OpenPositionForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(OpenPositionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Position
        exclude = ("created_by",)
