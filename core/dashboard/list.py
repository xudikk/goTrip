from django.shortcuts import redirect, render
from core.models.auth import User


def list_user(request):
    users = User.objects.all()
    return render(request, 'pages/list.html', {'root': users})
