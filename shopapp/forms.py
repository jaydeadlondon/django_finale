from django import forms
from django.contrib.auth.models import User
from .models import Product, Order


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV файл",
        help_text="Выберите CSV файл для импорта заказов"
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount', 'archived']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название продукта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание продукта'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': '0'
            }),
            'archived': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        labels = {
            'name': 'Название',
            'description': 'Описание',
            'price': 'Цена (руб.)',
            'discount': 'Скидка (%)',
            'archived': 'Архивировано'
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля')
        return price

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount and (discount < 0 or discount > 100):
            raise forms.ValidationError('Скидка должна быть от 0 до 100%')
        return discount


class OrderForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Покупатель',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Выберите покупателя'
    )

    class Meta:
        model = Order
        fields = ['user', 'products', 'delivery_address', 'promocode']

        widgets = {
            'products': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введите адрес доставки'
            }),
            'promocode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Промокод (если есть)'
            })
        }

        labels = {
            'products': 'Товары',
            'delivery_address': 'Адрес доставки',
            'promocode': 'Промокод'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].queryset = Product.objects.filter(archived=False)

    def clean_products(self):
        products = self.cleaned_data.get('products')
        if not products:
            raise forms.ValidationError('Выберите хотя бы один товар')
        return products