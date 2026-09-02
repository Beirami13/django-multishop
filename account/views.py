from django.shortcuts import render
from django.views import View

from .forms import UserLoginForm


class UserLogin(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request,'account/login.html',{'form': form})