from posts.views import BaseView, CreatePostView, PostDelete, PostDetail, PostUpdate
from django.urls import path, re_path
from django.urls.conf import include
from .api import urls

urlpatterns = [
    path('', BaseView.as_view(), name = 'index'),
    path('api/', include(urls)),
    path('post/add/', CreatePostView.as_view(), name='post-create'),
    path('post/<slug>/', PostDetail.as_view(), name = 'post-detail'),
    path('post/<slug>/update/', PostUpdate.as_view(), name = 'post-update'),
    path('post/<slug>/delete/', PostDelete.as_view(), name='post-delete'),
]
