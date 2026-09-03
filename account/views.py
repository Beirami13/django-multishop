from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View

from .forms import UserLoginForm


class UserLogin(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['phone_number'], password=cd['password'])
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                form.add_error('password', "invalid data")
        else:
            form.add_error('password', "invalid data")

        return render(request, 'account/login.html', {'form': form})
