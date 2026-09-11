from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import View
from .forms import UserLoginForm, RegisterForm, CheckOtpForm
import ghasedak_sms
from random import randint
from .models import otp, User
from uuid import uuid4

SMS = ghasedak_sms.Ghasedak("API", '09924631590')


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


class UserRegister(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'account/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            rand_code = randint(1000, 9999)
            token = str(uuid4())

            SMS.send_single_sms(
                ghasedak_sms.SendSingleSmsInput(
                    message=rand_code,
                    receptor=cd['phone_number'],
                    line_number='3000****',
                    send_date='',
                    client_reference_id=''
                )
            )

            otp.objects.create(
                phone_number=cd['phone_number'],
                code=rand_code,
                token=token,
            )

            return redirect(
                reverse('account:check_otp') + f'?token={token}'
            )

        form.add_error('password', "invalid data")

        return render(request, 'account/register.html', {'form': form})


class CheckOtpView(View):
    def get(self, request):
        form = CheckOtpForm()

        return render(
            request,
            'account/checkCode.html',
            {'form': form}
        )

    def post(self, request):
        token = request.GET.get('token')

        form = CheckOtpForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            otp_obj = otp.objects.filter(
                code=cd['code'],
                token=token
            ).first()

            if otp_obj:
                user, is_create = User.objects.get_or_create(
                    phone_number=otp_obj.phone_number
                )

                login(request, user)

                return redirect('/')

            form.add_error('code', 'wrong code')
            otp_obj.delete()

        return render(
            request,
            'account/checkCode.html',
            {'form': form}
        )