from django.views.generic import ListView
from .models import Article


class ArticlesListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return (
            Article.objects
            .select_related('author', 'category')       # JOIN для FK
            .prefetch_related('tags')                   # отдельный запрос для M2M
            .defer('content')                           # не грузим content
            .order_by('-pub_date')
        )