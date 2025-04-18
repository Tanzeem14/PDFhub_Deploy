import jwt
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def login_required_jwt(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get("jwt_token")
        if not token:
            messages.error(request, "Please log in to access this page")
            return redirect("login")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            request.jwt_user = payload
        except jwt.ExpiredSignatureError:
            messages.error(request, "Session expired. Please log in again.")
            return redirect("login")
        except jwt.InvalidTokenError:
            messages.error(request, "Invalid token. Please log in again.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
