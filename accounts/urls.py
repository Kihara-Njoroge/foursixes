from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signin/', views.signin, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
]
