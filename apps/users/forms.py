from django import forms

from .models import Debtor


class DebtorForm(forms.ModelForm):
    class Meta:
        model = Debtor
        fields = ['name', 'whatsapp', 'trust_level']
        widgets = {
            'name': forms.TextInput(attrs={'autofocus': True}),
            'whatsapp': forms.TextInput(attrs={'placeholder': '+55 99 99999-9999'}),
            'trust_level': forms.Select(),
        }
