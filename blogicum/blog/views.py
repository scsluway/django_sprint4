from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy, reverse

from . import mixins
from .forms import UserForm, CommentForm
from .models import Post, Category, Comment
from .utils import query_config, display_config
from blogicum.settings import NUMBER_OF_POSTS

User = get_user_model()


def index(request):
    return render(
        request,
        'blog/index.html',
        {'page_obj': display_config.paginate_posts(
            request,
            query_config.filter_posts(filters=True, annotate_on=True)
        )}
    )


def post_detail(request, post_id):
    post = get_object_or_404(query_config.filter_posts(), pk=post_id)
    if request.user != post.author and (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > timezone.now()
    ):
        raise Http404
    context = {}
    if request.user.is_authenticated:
        context['form'] = CommentForm()
    context['post'] = post
    context['comments'] = post.comments.select_related('post', 'author')
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = query_config.filter_posts(
        category.posts,
        filters=True,
        annotate_on=True
    )
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': display_config.paginate_posts(request, posts)
        }
    )


class PostCreateView(
        mixins.PostSameSettingsMixin,
        LoginRequiredMixin,
        CreateView
):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(
        mixins.PostSameSettingsMixin,
        mixins.PostsAuthorMixin,
        UpdateView
):
    pk_url_kwarg = 'post_id'


class PostDeleteView(
        mixins.PostSameSettingsMixin,
        mixins.PostsAuthorMixin,
        DeleteView
):
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = NUMBER_OF_POSTS

    def get_queryset(self):
        author = get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwarg]
        )
        if author != self.request.user:
            return query_config.filter_posts(
                author.posts,
                filters=True,
                annotate_on=True
            )
        return query_config.filter_posts(author.posts, annotate_on=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwarg]
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    pk_url_kwarg = 'post_id'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post.objects,
            pk=self.kwargs[self.pk_url_kwarg]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class CommentUpdateView(
        mixins.CommentSameSettingsMixin,
        mixins.CommentsAuthorMixin,
        UpdateView
):
    pass


class CommentDeleteView(
        mixins.CommentSameSettingsMixin,
        mixins.CommentsAuthorMixin,
        DeleteView
):
    pass


class RegistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html',
    form_class = UserCreationForm,
    success_url = reverse_lazy('blog:index'),
