from functools import wraps
from django.shortcuts import redirect

from accounts.models import Student


def role_required(*allowed_roles):
    """Redirige al panel correcto si el rol no coincide."""

    allowed = set(allowed_roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            user = request.user
            role = getattr(user, "role", Student.Role.STUDENT)
            if role in allowed:
                return view_func(request, *args, **kwargs)
            if Student.Role.ADMIN in allowed and user.is_superuser:
                return view_func(request, *args, **kwargs)
            return redirect(user.get_dashboard_url_name())

        return _wrapped

    return decorator
