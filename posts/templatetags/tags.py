from django import template
from django.utils.html import html_safe
from posts.models import Post

register = template.Library()

@register.filter
def thumb_image_with_edit_form(url):
    html = f'''
        <img src="{url}" class="img-thumbnail" />
    '''
    return html


@register.filter
def checking_user_for_author(user, post):
    check = Post.objects.filter(pk=post.pk, user=user).exists()
    return check