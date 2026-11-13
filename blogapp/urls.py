from django.urls import path
from . import views

app_name = 'blogapp'

urlpatterns = [
    path('articles/', views.ArticlesListView.as_view(), name='article_list'),
]