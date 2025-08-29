from django.views.generic import ListView
from .models import Article
import logging

logger = logging.getLogger(__name__)


class ArticlesListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        logger.info("Запрос списка статей")
        return Article.objects.select_related(
            'author',
            'category'
        ).prefetch_related(
            'tags'
        ).defer(
            'content'
        )