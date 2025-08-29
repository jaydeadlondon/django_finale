from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        max_length=254,
        help_text='Обязательное поле. Введите действительный email.',
        required=True
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Необязательное поле.',
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Необязательное поле.',
        label='Фамилия'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
        }


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля"""
    class Meta:
        model = Profile
        fields = ['bio', 'birth_date', 'avatar', 'phone']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'bio': 'О себе',
            'birth_date': 'Дата рождения',
            'avatar': 'Аватар',
            'phone': 'Телефон',
        }