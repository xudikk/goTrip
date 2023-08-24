#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

from django.urls import path, include
from .view import index
from .auth import sign_in, otp, resent_otp, sign_out
from .list import list_user
urlpatterns = [
    path("", index, name='home'),
    path("login/", sign_in, name='login'),
    path('otp/', otp, name='otp'),
    path('re-otp/', resent_otp, name='re-otp'),
    path('logout/', sign_out, name='log_out'),
    path('user/list/', list_user, name='user_list'),
]
