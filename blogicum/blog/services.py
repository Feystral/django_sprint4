from django.db.models import Count
from django.core.paginator import Paginator
from django.utils import timezone


def annotate_and_select_related(queryset):

    return queryset.annotate(num_comments=Count('comments')).select_related(
        'author', 'location', 'category'
    ).order_by('-pub_date')


def filter_published_posts(queryset):

    return queryset.filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
        is_published=True
    )


def paginate_queryset(queryset, request, per_page):

    page_number = request.GET.get('page')
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
