from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name='accounts/login.html',
            redirect_authenticated_user=True,
            next_page='/',
        ),
        name='login',
    ),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),   # ← ключевая строка
    path('logout-done/', views.LogoutDoneView.as_view(), name='logout_done'),

    path('cookies/read/', views.CookieReadView.as_view(), name='cookie_read'),
    path('cookies/set/', views.CookieSetView.as_view(), name='cookie_set'),

    path('session/read/', views.SessionReadView.as_view(), name='session_read'),
    path('session/set/', views.SessionSetView.as_view(), name='session_set'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('about-me/', views.AboutMeView.as_view(), name='about_me'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile_update'),
]