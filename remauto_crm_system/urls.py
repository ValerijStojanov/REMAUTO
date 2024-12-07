from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.authorization, name='authorization'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hello/', views.hello_world, name='hello_world'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
