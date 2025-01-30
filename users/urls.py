from django.urls import path
from users.views import login, registration, profile, logout, edit_profile


app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('registration/', registration, name='registration'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('logout/', logout, name='logout'),
]