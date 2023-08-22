#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from django.urls import path, include
from .view import index

urlpatterns = [
    path("", index, name='home')
]