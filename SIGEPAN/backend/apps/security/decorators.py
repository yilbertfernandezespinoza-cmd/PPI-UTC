from functools import wraps
from django.shortcuts import redirect


def login_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if "usuario_id" not in request.session:

            return redirect("security:login")

        return view_func(request, *args, **kwargs)

    return wrapper