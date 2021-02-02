from django.urls import path

from . import views

urlpatterns = [
    path('', views.invalid_parameters, name='invalid_parameters'),  # invalid request
    path('user/{id}/', views.user, name='user_api'),     # get a user information
    path('host/', views.host, name='host_api'),     # get a host information
    path('login/', views.login, name='login'),      # TODO implement a login
]