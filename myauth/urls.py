from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

app_name = 'myauth'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('login/', LoginView.as_view(
        template_name='myauth/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', views.MyLogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('about-me/', views.about_me_view, name='about_me'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profile_update'),

    path('profile/', views.about_me_view, name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),

    path('cookie/set/', views.set_cookie_view, name='cookie_set'),
    path('cookie/get/', views.get_cookie_view, name='cookie_get'),
    path('session/set/', views.set_session_view, name='session_set'),
    path('session/get/', views.get_session_view, name='session_get'),
]