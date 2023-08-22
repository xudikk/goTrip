#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

from django.shortcuts import redirect, render


def index(request):

    return render(request, 'pages/index.html')
