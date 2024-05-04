from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from blog.forms import PostForm, CommentForm
from blog.models import Post, Comment


class PostsAuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if post.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().dispatch(request, *args, **kwargs)


class CommentsAuthorMixin:
    def dispatch(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        comment = get_object_or_404(
            Comment,
            pk=self.kwargs[self.pk_url_kwarg],
            post__id=post_id
        )
        if comment.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id
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
            kwargs={'post_id': self.kwargs.get('post_id')}
        )
