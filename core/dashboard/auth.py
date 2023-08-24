import datetime
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from methodism import code_decoder

from core.models import User, Otp


def loginn(requests):
    if not requests.user.is_anonymous:
        return redirect("home")

    if requests.POST:
        data = requests.POST
        user = User.objects.filter(phone=data['phone']).first()
        if not user:
            return render(requests, 'pages/auth/login.html', {"error": "Phone xato"})

        if not user.check_password(data['pass']):
            return render(requests, 'pages/auth/login.html', {"error": "Parol xato"})

        if not user.is_active:
            return render(requests, 'pages/auth/login.html', {"error": "Profil active emas "})

        code = random.randint(100000, 999999)
        key = code_decoder(code)

        a = Otp.objects.create(
            key=key,
            mobile=user.phone,
            step="login",
        )

        requests.session['user_id'] = a.id
        requests.session['otp_token'] = a.key
        requests.session['code'] = code
        requests.session['phone'] = a.mobile
        return redirect('otp')
    return render(requests, 'pages/auth/login.html')


def otp(request):
    if not request.session.get("otp_token"):
        return redirect("login")

    if request.POST:
        otp = Otp.objects.filter(key=request.session["otp_token"]).first()
        code = request.POST['code']

        if not code.isdigit():
            return render(request, "pages/auth/otp.html", {"error": "Harflar kiritmang!!!"})

        if otp.is_expired:
            otp.step = "failed"
            otp.save()
            return render(request, "pages/auth/otp.html", {"error": "Token eskirgan!!!"})

        if (datetime.datetime.now() - otp.created).total_seconds() >= 120:
            otp.is_expired = True
            otp.save()
            return render(request, "pages/auth/otp.html", {"error": "Vaqt tugadi!!!"})

        if int(code_decoder(otp.key, decode=True, l=1)) != int(code):
            otp.tries += 1
            otp.save()
            return render(request, "pages/auth/otp.html", {"error": "Cod hato!!!"})

        user = User.objects.get(phone=request.session["phone"])
        otp.step = "logged"
        login(request, user)
        otp.save()

        del request.session["user_id"]
        del request.session["code"]
        del request.session["phone"]
        del request.session["otp_token"]

        return redirect("home")

    return render(request, "pages/auth/otp.html")


def resent_otp(request):
    if not request.session.get("otp_token"):
        return redirect("login")

    old = Otp.objects.filter(key=request.session["otp_token"]).first()
    old.step = 'failed'
    old.is_expired = True
    old.save()

    code = random.randint(100000, 999999)
    # send_sms(998951808802,code)
    key = code_decoder(code)

    otp = Otp.objects.create(
        key=key,
        mobile=old.mobile,
        step='login'
    )
    otp.save()

    request.session["code"] = code
    request.session["phone"] = otp.mobile
    request.session["otp_token"] = otp.key
    return redirect("otp")


@login_required(login_url='login')
def log_out(request):
    logout(request)
    return redirect("login")