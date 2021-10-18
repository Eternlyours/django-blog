from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.exceptions import ValidationError
from django.forms import fields, inlineformset_factory, models, widgets
from django.forms.forms import Form

from posts.models import Image, Post


class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}), max_length=255, required=True, label='Заголовок')
    body = forms.CharField(
        widget=CKEditorWidget(config_name='post_ckeditor'),
        required=True,
        label='Текст публикации'
    )
    images = forms.ImageField(widget=widgets.ClearableFileInput(
        attrs={
            'multiple': 'true',
            'id':       'multiple-image-post',
            'class':    'custom-hidden'
        }),
        label='Медиа',
        required=True)

    is_active = forms.CharField(widget=forms.CheckboxInput(
        attrs={'class': 'custom-control-input'}),
        label='Отображать',
        required=False, initial=True)

    private_mode = forms.CharField(widget=forms.CheckboxInput(
        attrs={'class': 'custom-control-input'}),
        label='Только для близких',
        required=False, initial=False)

    commentable = forms.CharField(widget=forms.CheckboxInput(
        attrs={'class': 'custom-control-input'}),
        label='Запретить комментирование',
        required=False, initial=False
    )

    def clean(self):
        data = super().clean()
        title = data.get('title', '')
        check_title = Post.objects.filter(title=title).exists()
        if check_title:
            self.add_error(
                'title', 'Придумайте другой заголовок! Этот уже существует')
        return data

    class Meta:
        model = Post
        exclude = ('created_at', 'updated_at', 'user', 'slug', )


class PostUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():        
            if type(visible.field.widget) == widgets.NullBooleanSelect:
                visible.field.widget = forms.CheckboxInput(attrs={'class': 'custom-control-input'})
            else:
                visible.field.widget.attrs.update({'class': 'form-control'})
    
    class Meta:
        model = Post
        widgets = {
            'body': CKEditorWidget(config_name='post_ckeditor'),
        }
        fields = ('title', 'body',
                  'private_mode', 'is_active', 'commentable',)

    def clean(self):
        data = super().clean()
        title = data.get('title', '')
        check_title = Post.objects.filter(title=title).exists()
        if check_title:
            self.add_error(
                'title', 'Придумайте другой заголовок! Этот уже существует')
        return data
        
    
class ImagesFormSet(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image', )
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


InlineFormsetPostImage = inlineformset_factory(Post, Image, form=ImagesFormSet, extra=3, )


class CommentForm(forms.Form):
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'), required=True, label='Комментарий')

    def clean(self):
        data = super().clean()
        text = data.get('text', '')
        if text in '<p>1</p>':
            self.add_error('text', 'error')
