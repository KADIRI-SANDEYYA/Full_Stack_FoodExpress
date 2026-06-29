from django import forms


class CheckoutForm(forms.Form):
    address = forms.CharField(
        min_length=10,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'House number, street, area, city',
        }),
    )
    phone = forms.CharField(
        min_length=10,
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': '10-digit mobile number',
        }),
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = phone.replace(' ', '').replace('-', '')
        if not digits.isdigit():
            raise forms.ValidationError('Enter a valid phone number using digits only.')
        return phone
