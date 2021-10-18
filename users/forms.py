from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm, forms.ModelForm):
    password = forms.CharField(
        widget = forms.PasswordInput, required = True, min_length = 4, label = u'Пароль')
    username = forms.CharField(required = True, label = u'Имя пользователя')

    class Meta:
        model = User
        fields = ('username', 'password')
