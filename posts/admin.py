from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from django.forms import fields

from .models import Comment, Image, Post

class PostAdminForm(forms.ModelForm):
    body = forms.CharField(
        widget=CKEditorWidget(config_name='post_ckeditor'),
        required=True
    )

    class Meta:
        model = Post
        fields = '__all__'


class ImageTabInlines(admin.TabularInline):
    model = Image


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    fields = ('slug', 'is_active', 'private_mode', 'title', 'body', 'user', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'slug')
    list_display = ('title', 'created_at', 'user')
    list_display_links = ('title',)
    inlines = (ImageTabInlines, )
    date_hierarchy = 'created_at'


admin.site.register(Image)
admin.site.register(Comment)