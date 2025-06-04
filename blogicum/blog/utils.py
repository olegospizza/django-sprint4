from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count

from blog.models import Post

POSTS_IN_PAGE = 10


def get_published_posts():
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def annotate_posts(queryset):
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def paginate_queryset(request, queryset, per_page=POSTS_IN_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
