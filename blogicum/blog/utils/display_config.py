from django.core.paginator import Paginator

from blogicum.settings import NUMBER_OF_POSTS


def paginate_posts(request, posts, number=NUMBER_OF_POSTS):
    paginator = Paginator(posts, number)
    return paginator.get_page(request.GET.get('page'))
