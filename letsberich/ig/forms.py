from django import forms

from letsberich.ig.models import Position, Autotrade


class OpenPositionForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(OpenPositionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Position
        exclude = ("created_by",)


class AutoTradeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AutoTradeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Autotrade
        fields = ['status']