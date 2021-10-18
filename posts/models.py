from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.defaultfilters import slugify
from unidecode import unidecode

from .managers import ProductManager


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=u'Создано')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=u'Редактировано')

    class Meta:
        abstract = True


class Tag(TimeStampMixin):
    tag = models.SlugField(verbose_name=u'Тег')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=u'Контент')
    object_id = models.PositiveIntegerField(verbose_name=u'Уникальный номер')
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.tag


class Post(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='posts', verbose_name=u'Пользователь')
    slug = models.SlugField(verbose_name=u'Семантический URL', unique=True)
    title = models.CharField(
        max_length=255, verbose_name=u'Заголовок публикации')
    body = models.TextField(verbose_name=u'Тело публикации')
    private_mode = models.BooleanField(
        verbose_name=u'Режим для близких', null=True, blank=True)
    is_active = models.BooleanField(
        verbose_name=u'Видимость', default=True, null=True, blank=True)
    tags = GenericRelation(Tag, related_name='tags',
                           related_query_name='product')
    commentable = models.BooleanField(
        verbose_name=u'Запретить комментирование',
        default=False, null=True, blank=True)

    comments = GenericRelation('Comment')

    objects = ProductManager()

    def counter_comments(self):
        return self.comments.count()

    def counter_views(self):
        return self.views.count()

    def __str__(self):
        return '{0} - {1}'.format(self.slug, self.user)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        return super().save(*args, **kwargs)

    @classmethod
    def create(cls, title, body, commentable, private_mode, is_active, user):
        post = cls(title=title, body=body, commentable=commentable, private_mode=private_mode, is_active=is_active, user=user)
        return post

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'


class PostViews(models.Model):
    viewer = models.ForeignKey(User, related_name='views', on_delete=models.CASCADE, verbose_name='Зритель')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views', verbose_name='Публикация')


class Image(models.Model):
    image = models.ImageField(
        upload_to='upload/image/post/%Y/%m/%d/', verbose_name=u'Картинка')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='images', verbose_name=u'Публикация')

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'

    def __str__(self):
        return self.image.url

    @classmethod
    def create(cls, image, post):
        image = cls(image=image, post=post)        
        return image


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария')
    text = models.TextField(verbose_name='Тект')
    created_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Дата редактирования', auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.author.username

    @classmethod
    def create(cls, author, text, content_object):
        comment = cls(author=author, text=text, content_object=content_object)
        return comment

