from django.shortcuts import render


def home(request):
    """
    Vista principal de SIGEPAN.
    """
    return render(request, "core/home.html")