from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from blog.models import Post, Category

NUMBER_OF_POSTS = 5


def filter_posts(manager=Post.objects):
    return manager.select_related(
        'category', 'author', 'location'
    ).filter(
        category__is_published=True,
        is_published=True,
        pub_date__lt=timezone.now()
    )


class HomePage(TemplateView):
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = filter_posts()[:NUMBER_OF_POSTS]
        return context


def post_detail(request, post_id):
    post = get_object_or_404(filter_posts(), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = filter_posts(category.posts)
    return render(
        request,
        'blog/category.html',
        {'category': category, 'post_list': posts}
    )
