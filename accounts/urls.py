from django.urls import path 
from accounts.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('' , home, name="home" ), 
    path('custom_login/' , login_page , name="custom_login" ),
    path('custom_register/' , register_page , name="custom_register"),
    path('accounts/activate/<email_token>/', activate_email, name="activate_email"),
    path('bookings/', bookings, name='bookings'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]

