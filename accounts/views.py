from django.views.generic import View, TemplateView, DetailView, ListView, UpdateView
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .forms import RegisterForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm
from django.shortcuts import get_object_or_404



class MyLogoutView(LogoutView):
    next_page = '/accounts/logout-done/'
    http_method_names = ['get', 'post', 'options']
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class LogoutDoneView(TemplateView):
    template_name = 'accounts/logout_done.html'


class CookieReadView(View):
    def get(self, request):
        value = request.COOKIES.get('my_cookie', 'значение по умолчанию')
        return HttpResponse(f'Cookie my_cookie = {value}')


class CookieSetView(View):
    def get(self, request):
        response = HttpResponse('Cookie my_cookie установлена в "hello_cookie"')
        response.set_cookie('my_cookie', 'hello_cookie', max_age=3600, httponly=True)
        return response


class SessionReadView(View):
    def get(self, request):
        value = request.session.get('my_session_key', 'значение по умолчанию')
        return HttpResponse(f'Session my_session_key = {value}')


class SessionSetView(View):
    def get(self, request):
        request.session['my_session_key'] = 'hello_session'
        request.session.modified = True
        return HttpResponse('Session my_session_key установлена в "hello_session"')


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

class AboutMeView(LoginRequiredMixin, UpdateView):
    model = Profile
    fields = ("avatar",)
    template_name = "accounts/about_me.html"
    success_url = reverse_lazy("accounts:about_me")

    def get_object(self, queryset=None):
        return self.request.user.profile

class UserListView(ListView):
    """Список всех пользователей."""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.select_related('profile').order_by('username')


class UserDetailView(DetailView):
    """Детали профиля любого пользователя."""
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'profile_user'

    def get_queryset(self):
        return User.objects.select_related('profile')


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление профиля. Только владелец или is_staff."""
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:about_me')

    def get_object(self, queryset=None):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return user.profile

    def test_func(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return self.request.user.is_staff or self.request.user == user

    def get_success_url(self):
        # после сохранения вернуть на страницу того пользователя, чей профиль правили
        return reverse_lazy('accounts:user_detail', kwargs={'pk': self.kwargs['pk']})