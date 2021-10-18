from .views import ImageApiView, ImageUpload, UserApiCreateView, UserApiListView, PostApiListCreateView
from django.urls import path

urlpatterns = [
    path('posts/', PostApiListCreateView.as_view(), name='posts'),
    path('posts/create/', ImageUpload, name='posts-create'),
    path('users/', UserApiListView.as_view(), name='users'),    
    path('users/create/', UserApiCreateView.as_view(), name='users'),    
    path('images/', ImageApiView.as_view()),
]