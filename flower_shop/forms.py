from django import forms
from phonenumber_field.formfields import PhoneNumberField


class ConsultationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'order__form_input',
            'placeholder': 'Введите Имя'
        })
    )

    phone = PhoneNumberField(
        region='RU',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'order__form_input',
            'placeholder': '+ 7 (999) 000 00 00'
        })
    )

    agreement = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'singUpConsultation__ckekbox'
        })
    )
