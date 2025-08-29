from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import datetime
from .forms import SignUpForm, ProfileForm
from .models import Profile


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            print(f"User {request.user.username} is logging out")
        return super().dispatch(request, *args, **kwargs)


class HomeView(TemplateView):
    template_name = 'myauth/home.html'


class SignUpView(CreateView):
    """Регистрация нового пользователя"""
    form_class = SignUpForm
    template_name = 'myauth/signup.html'
    success_url = reverse_lazy('myauth:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def get_or_create_profile(user):
    """Получает или создаёт профиль для пользователя"""
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        print(f"Создан профиль для пользователя {user.username}")
    return profile


@login_required
def about_me_view(request):
    """Страница about-me текущего пользователя"""
    profile = get_or_create_profile(request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('myauth:about_me')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'myauth/about_me.html', {
        'user': request.user,
        'profile': request.user.profile,
        'form': form
    })


class UserListView(ListView):
    """Список всех пользователей"""
    model = User
    template_name = 'myauth/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        for user in User.objects.filter(profile__isnull=True):
            Profile.objects.create(user=user)

        return User.objects.select_related('profile').filter(is_active=True)


class UserDetailView(DetailView):
    """Детали профиля пользователя"""
    model = User
    template_name = 'myauth/user_detail.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        get_or_create_profile(user)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile_user = self.object

        can_edit = (
                user.is_authenticated and
                (user.is_staff or user == profile_user)
        )
        context['can_edit'] = can_edit
        return context


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновление профиля пользователя"""
    model = Profile
    form_class = ProfileForm
    template_name = 'myauth/profile_update.html'

    def test_func(self):
        """Проверка прав на редактирование"""
        profile = self.get_object()
        user = self.request.user
        # Может редактировать: владелец профиля или staff
        return user.is_staff or user == profile.user

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для редактирования этого профиля")

    def get_object(self, queryset=None):
        # Получаем профиль по pk пользователя из URL
        user_pk = self.kwargs.get('pk')
        return get_object_or_404(Profile, user__pk=user_pk)

    def get_success_url(self):
        return reverse('myauth:user_detail', kwargs={'pk': self.object.user.pk})


def set_cookie_view(request):
    """View для установки данных в cookies"""
    response = render(request, 'myauth/cookie_set.html')

    response.set_cookie(
        'username_cookie',
        request.user.username if request.user.is_authenticated else 'anonymous',
        max_age=3600
    )

    response.set_cookie(
        'last_visit',
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        max_age=86400
    )

    response.set_cookie(
        'visit_count',
        int(request.COOKIES.get('visit_count', 0)) + 1,
        max_age=86400 * 30
    )

    return response


def get_cookie_view(request):
    """View для чтения данных из cookies"""
    username_cookie = request.COOKIES.get('username_cookie', 'Не установлено')
    last_visit = request.COOKIES.get('last_visit', 'Первый визит')
    visit_count = request.COOKIES.get('visit_count', '0')

    all_cookies = request.COOKIES

    context = {
        'username_cookie': username_cookie,
        'last_visit': last_visit,
        'visit_count': visit_count,
        'all_cookies': all_cookies,
    }

    return render(request, 'myauth/cookie_get.html', context)



def set_session_view(request):
    """View для установки данных в session"""
    request.session['username_session'] = request.user.username if request.user.is_authenticated else 'guest'
    request.session['last_activity'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    request.session['page_views'] = request.session.get('page_views', 0) + 1

    request.session['user_preferences'] = {
        'theme': 'dark',
        'language': 'ru',
        'notifications': True
    }

    request.session.set_expiry(3600)

    context = {
        'session_data': dict(request.session),
        'session_key': request.session.session_key,
    }

    return render(request, 'myauth/session_set.html', context)


def get_session_view(request):
    """View для чтения данных из session"""
    username_session = request.session.get('username_session', 'Не установлено')
    last_activity = request.session.get('last_activity', 'Нет данных')
    page_views = request.session.get('page_views', 0)
    user_preferences = request.session.get('user_preferences', {})

    session_info = {
        'session_key': request.session.session_key,
        'is_empty': request.session.is_empty(),
        'expiry_age': request.session.get_expiry_age(),
        'expiry_date': request.session.get_expiry_date(),
    }

    context = {
        'username_session': username_session,
        'last_activity': last_activity,
        'page_views': page_views,
        'user_preferences': user_preferences,
        'session_info': session_info,
        'all_session_data': dict(request.session),
    }

    return render(request, 'myauth/session_get.html', context)