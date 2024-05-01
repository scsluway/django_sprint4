from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy, reverse

from blog.forms import PostForm, UserForm, CommentForm
from blog.models import Post, Category, Comment

NUMBER_OF_POSTS = 10

User = get_user_model()


class OnlyAuthorMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.pk_url_kwarg == 'post_id':
            post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
            if post.author != self.request.user:
                return redirect(
                    'blog:post_detail',
                    post_id=self.kwargs[self.pk_url_kwarg]
                )
        else:
            comment = get_object_or_404(
                Comment,
                pk=self.kwargs[self.pk_url_kwarg]
            )
            if comment.author != self.request.user:
                return redirect(
                    'blog:post_detail',
                    post_id=self.get_object().post.id
                )
        return super().dispatch(request, *args, **kwargs)


class PostSameSettingsMixin:
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm


class CommentSameSettingsMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().post.id}
        )


def filter_posts(manager=Post.objects, request=None):
    return manager.select_related(
        'category', 'author', 'location'
    ).filter(
        category__is_published=True,
        is_published=True,
        pub_date__lt=timezone.now()
    ).annotate(comment_count=Count('comments'))


def index(request):
    # Не работает сортировка описанная в мета классе модели.
    paginator = Paginator(
        filter_posts().order_by('-pub_date'),
        NUMBER_OF_POSTS
    )
    return render(
        request,
        'blog/index.html',
        {'page_obj': paginator.get_page(request.GET.get('page'))}
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects, pk=post_id)
    if request.user != post.author:
        post = get_object_or_404(filter_posts(), pk=post_id)
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
    paginator = Paginator(
        filter_posts(category.posts).order_by('-pub_date'),
        NUMBER_OF_POSTS
    )
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': paginator.get_page(request.GET.get('page'))
        }
    )


class PostCreateView(PostSameSettingsMixin, LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostSameSettingsMixin, OnlyAuthorMixin, UpdateView):
    pk_url_kwarg = 'post_id'


class PostDeleteView(PostSameSettingsMixin, OnlyAuthorMixin, DeleteView):
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
        self.author = get_object_or_404(
            User,
            username=self.kwargs[self.slug_url_kwarg]
        )
        if self.author != self.request.user:
            return filter_posts(
                self.author.posts,
                self.request
            ).order_by('-pub_date')
        return self.author.posts.select_related(
            'category',
            'location'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context

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


class CommentUpdateView(CommentSameSettingsMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentSameSettingsMixin, OnlyAuthorMixin, DeleteView):
    pass
