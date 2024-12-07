from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, Service, Client


class AccountCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['username', 'email', 'first_name', 'last_name']

class ClientForm(forms.ModelForm):
    # Поле для выбора услуг
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.SelectMultiple,
        required=False,
        label="Выберите услуги"
    )

    class Meta:
        model = Client
        fields = ['name', 'surname', 'phone_number', 'email']  # Поля из модели Client
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Введите имя'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Введите фамилию'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Введите номер телефона'}),
            'email': forms.TextInput(attrs={'placeholder': 'Введите мейл'}),
        }
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'phone_number': 'Телефон',
            'email': 'Мейл'
        }
        
class AddServiceForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label="Выберите услугу",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )