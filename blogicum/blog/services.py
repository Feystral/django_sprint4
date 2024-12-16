from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone


def annotate_with_comment_count(queryset):
    return queryset.annotate(num_comments=Count('comments'))


def filter_published_posts(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
        is_published=True
    ).select_related('author', 'location', 'category').order_by('-pub_date')


def paginate_queryset(queryset, page_number, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
