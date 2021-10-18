from django.contrib.contenttypes.models import ContentType
from .models import Comment, Image, Post


def create_post(request, data) -> None:
    data = clean_post_form(request, data)
    post = Post.create(**data)
    post.save()
    images = request.FILES.getlist('images')
    for i in images:
        image = Image.create(i, post)
        image.save()


def create_comment(request, data, obj) -> None:
    text = data['text']
    comment = Comment.create(author=request.user, 
        text=text, content_object=obj)
    comment.save()


def clean_post_form(request, data):
    del data['images']
    data['user'] = request.user
    return data


def get_content_type(model):
    return ContentType.objects.get(model=model)
