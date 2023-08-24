#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from django.urls import path, include
from .view import index
from .auth import loginn, otp, resent_otp, log_out

urlpatterns = [
    path("", index, name='home'),
    path("login/", loginn, name='login'),
    path('otp/', otp, name='otp'),
    path('re-otp/', resent_otp, name='re-otp'),
    path('logout/', log_out, name='log_out')
]