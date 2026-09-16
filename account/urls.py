from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('login', views.UserLogin.as_view(), name='login'),
    path('register', views.UserRegister.as_view(), name='register'),
    path('check', views.CheckOtpView.as_view(), name='check_otp'),
    path('logout', views.UserLogout, name='logout'),
    path('add/address', views.AddAddressView.as_view(), name='add_address'),
]