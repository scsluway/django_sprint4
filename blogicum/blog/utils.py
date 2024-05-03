from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from blog.models import Post
from blogicum.settings import NUMBER_OF_POSTS


def filter_posts(manager=Post.objects, filters=False, sorting=False):
    posts = manager.select_related(
        'category', 'author', 'location'
    )
    if filters:
        posts = posts.filter(
            category__is_published=True,
            is_published=True,
            pub_date__lt=timezone.now()
        )
    if sorting:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return posts


def paginate_posts(request, posts, number=NUMBER_OF_POSTS):
    paginator = Paginator(posts, number)
    return paginator.get_page(request.GET.get('page'))
