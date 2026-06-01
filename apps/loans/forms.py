from django import forms
from django.forms import inlineformset_factory
from .models import Loan, LoanPayment
from datetime import datetime, timedelta


class LoanForm(forms.ModelForm):
    """Form para criar/editar empréstimos"""
    
    class Meta:
        model = Loan
        fields = [
            'debtor',
            'amount_borrowed',
            'loan_date',
            'due_date',
            'interest_rate',
            'num_installments',
            'first_payment_date',
            'status',
            'notes',
        ]
        widgets = {
            'loan_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'first_payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'debtor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'amount_borrowed': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ex: 5.00'
            }),
            'num_installments': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Filtra devedores apenas da empresa atual
        if self.company:
            self.fields['debtor'].queryset = self.company.debtors.all()


class LoanPaymentForm(forms.ModelForm):
    """Form para registrar pagamentos"""
    
    class Meta:
        model = LoanPayment
        fields = [
            'status',
            'paid_date',
            'paid_amount',
            'notes',
        ]
        widgets = {
            'paid_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'paid_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
        }


# Formset para gerenciar múltiplos pagamentos
LoanPaymentFormSet = inlineformset_factory(
    Loan,
    LoanPayment,
    form=LoanPaymentForm,
    extra=1,
    can_delete=True
)
