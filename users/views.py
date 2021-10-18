import django
from users.forms import LoginForm
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView


class LoginCustomView(LoginView):
    template_name = 'Auth/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('index')

    def get_success_url(self):
        return self.success_url


class LogoutCustomView(LogoutView):
    next_page = reverse_lazy('index')