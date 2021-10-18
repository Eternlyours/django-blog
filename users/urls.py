from users.views import LoginCustomView, LogoutCustomView
from django.urls import path

urlpatterns = [
    path('login/', LoginCustomView.as_view(), name = 'login'),
    path('logout/', LogoutCustomView.as_view(), name = 'logout'),
]
