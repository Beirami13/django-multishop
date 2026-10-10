from django import forms

from account.models import Address
from account.validator import phone


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20, validators=[phone])
    email = forms.EmailField(required=False)
    address = forms.ModelChoiceField(queryset=Address.objects.none())
    payment_method = forms.ChoiceField(
        choices=[('cash', 'Cash on Delivery'), ('online', 'Online Payment')]
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = Address.objects.filter(user=user)