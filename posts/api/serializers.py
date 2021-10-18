from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import Image, Post


class ImageSerializer(serializers.Serializer):
    class Meta:
        model = Image
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id', 'slug', 'title', 'body', 'images',
                  'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        post = Post.objects.create(**validated_data)
        for image_data in images_data:
            Image.objects.create(post=post, **image_data)
        return post


class UserSerializer(serializers.HyperlinkedModelSerializer):
    posts = PostSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'posts')
