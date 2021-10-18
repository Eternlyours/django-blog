import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.http import response
from django.http.request import HttpRequest
from django.http.response import (HttpResponse, HttpResponseForbidden,
                                  HttpResponseRedirect, JsonResponse)
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)
from django.views.generic.base import View
from django.views.generic.edit import (DeleteView, FormMixin, FormView,
                                       ModelFormMixin)

from posts.forms import (CommentForm, InlineFormsetPostImage, PostForm,
                         PostUpdateForm)
from posts.models import Comment, Post, PostViews

from .services import create_comment, create_post, get_content_type
from .templatetags.tags import checking_user_for_author


class FormJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, InMemoryUploadedFile):
            return o.read()
        return str(o)


class JSONResponsableFormMixin(FormMixin):

    def form_valid(self, form):
        response = json.dumps(form.cleaned_data, cls=FormJSONEncoder)
        return JsonResponse({'data': response}, status=200, content_type='application/json')

    def form_invalid(self, form):        
        response = json.dumps(form.errors)
        return JsonResponse({'errors': response}, content_type='application/json', status=400)


class CreatePostView(JSONResponsableFormMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'Post/add-post.html'

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        create_post(self.request, form.cleaned_data)
        return super().form_valid(form)


# class CreatePostView(FormView):
#     model = Post
#     form_class = PostForm
#     success_url = reverse_lazy('index')
#     template_name = 'Post/add-post.html'

#     @method_decorator(login_required(login_url=reverse_lazy('login')))
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)

#     def form_valid(self, form):
#         data = form.cleaned_data
#         create_post(self.request, data)
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         return self.render_to_response(self.get_context_data(form=form))


class BaseView(ListView):
    template_name = 'index.html'
    form_class = PostForm
    queryset = Post.objects.get_posts()
    # success_url = reverse_lazy('index')
    paginate_by = 7

    # def dispatch(self, request, *args, **kwargs):
    #     self.object_list = self.get_queryset()
    #     return super().dispatch(request, *args, **kwargs)

    # def form_valid(self, form):
    #     if not self.request.user.is_authenticated:
    #         messages.add_message(self.request, messages.INFO,
    #                              'Авторизуйтесь пожалуйста')
    #         return HttpResponseRedirect(reverse('index'))
    #     data = form.cleaned_data
    #     create_post(self.request, data)
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     return self.render_to_response(self.get_context_data(form=form, object_list=self.object_list))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная'
        context['form'] = PostForm
        return context


class PostDelete(DeleteView):
    queryset = Post.objects.get_posts()
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        self.obj = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not checking_user_for_author(request.user, self.obj):
            # return HttpResponseRedirect(self.get_success_url())
            return HttpResponseForbidden()
        return super().get(request, *args, **kwargs)


class PostDetail(DetailView, FormView):
    queryset = Post.objects.get_posts()
    template_name = 'Post/detail.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('post-detail', kwargs={'slug': self.object.slug})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            PostViews.objects.get_or_create(
                viewer=request.user,
                post=self.object
            )
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def post(self, request, *args, **kwargs):
        if self.object.commentable:
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        create_comment(self.request, data, self.object)
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type = get_content_type('post')
        context['comments'] = Comment.objects.all().select_related('author').filter(
            content_type=content_type, object_id=self.object.id).order_by('-created_at')
        return context


class PostUpdate(UpdateView):
    template_name = 'Post/update-post.html'
    queryset = Post.objects.get_posts()
    template_name_suffix = '_update_form'
    form_class = PostUpdateForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def get(self, request, *args, **kwargs):
        if not checking_user_for_author(user=request.user, post=self.object):
            return HttpResponseRedirect(self.get_success_url())
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('post-detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = InlineFormsetPostImage(
            instance=self.object)
        return context

    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def post(self, request, *args, **kwargs):
        if not checking_user_for_author(user=request.user, post=self.object):
            return HttpResponseRedirect(self.get_success_url())
        form = self.get_form()
        formset = InlineFormsetPostImage(
            request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            if formset.is_valid():
                formset.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)       

    def form_valid(self, form):
        super().form_valid(form)
        form.save()
        return HttpResponseRedirect(self.get_success_url())

