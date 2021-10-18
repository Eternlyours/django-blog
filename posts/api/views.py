from django.contrib.auth.models import User
from django.db.models import query
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework import permissions, viewsets
from ..models import Image, Post
from .serializers import ImageSerializer, PostSerializer, UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class UserApiListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class UserApiCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class PostApiListCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        permissions.AllowAny
    ]


# class PostApiCreateView(CreateAPIView):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]


class ImageApiView(ListAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser, )
    permission_classes = [
        permissions.AllowAny
    ]


class ImageUpload(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser, )

    def perform_create(self, serializer):
        serializer.save(image=self.request.data.get('image'))
