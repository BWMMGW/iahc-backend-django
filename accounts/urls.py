from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('check_session', views.check_session, name='check_session'),
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('recovery', views.recovery_view, name='recovery'),
    path('api/profile/<str:username>', views.get_profile, name='profile'),
    path('profile/<str:username>/edit', views.edit_profile, name='edit_profile'),
    path('logout', views.logout_view, name='logout'),
    path('api/search', views.search_users, name='search_users'),   # NEW
]
