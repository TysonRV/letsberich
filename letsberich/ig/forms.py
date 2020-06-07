from django import forms
from letsberich.ig.models import Position


class OpenPositionForm(forms.ModelForm):
    currencyCode = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': '3 letter id'}), initial='BTC')
    dealReference = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'User set Deal Ref'}), initial='TestPOS11')
    direction = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'BUY or SELL'}), initial='BUY')
    epic = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'EPIC'}), initial='CS.D.BITCOIN.TODAY.IP')
    expiry = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'Expiry Date'}), initial='21-JUL-20')
    forceOpen = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'true or false'}), initial='true')
    guaranteedStop = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'true or false'}), initial='false')
    orderType = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'LIMIT, MARKET or QUOTE'}), initial='MARKET')
    size = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'order size'}), initial='0.6')
    stopLevel = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 1, 'placeholder': 'Stop Level [GBP]'}), initial='9325')


    class Meta:
        model = Position
        fields = ['currencyCode', 'dealReference', 'direction', 'epic', 'expiry',
                  'forceOpen', 'guaranteedStop',  'orderType', 'size', 'stopLevel']