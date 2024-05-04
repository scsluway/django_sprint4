from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def filter_posts(manager=Post.objects, filters=False, annotate_on=False):
    posts = manager.select_related(
        'category', 'author', 'location'
    )
    if filters:
        posts = posts.filter(
            category__is_published=True,
            is_published=True,
            pub_date__lt=timezone.now()
        )
    if annotate_on:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return posts
