from django.urls import path
from home import views
from home.views import HomeView

app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]