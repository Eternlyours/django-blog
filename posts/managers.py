from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from django.db.models.aggregates import Count
from django.db.models.query import Prefetch
from django.db.models import Subquery, OuterRef


class ProductManager(Manager):

    def get_posts(self):
        Image = apps.get_model('posts', 'Image')
        Comment = apps.get_model('posts', 'Comment')

        image_qs = Image.objects.select_related('post').all()
        posts = self.filter(is_active=True).all()

        posts = posts.prefetch_related(
            Prefetch(
                'images',
                queryset=image_qs
            )
        )
        posts = posts.select_related('user')
        posts = posts.prefetch_related('comments')
        posts = posts.order_by('-created_at')

        return posts
