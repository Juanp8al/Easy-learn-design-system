from django.urls import reverse

from accounts.models import Student
from accounts.notifications import get_portal_notifications

_ROLE_LABELS = {
    Student.Role.STUDENT: "Estudiante",
    Student.Role.TEACHER: "Docente",
    Student.Role.ADMIN: "Administrador",
}


def portal_notifications(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    items, unread = get_portal_notifications(request.user)
    return {
        "portal_notifications": items,
        "portal_notifications_unread": unread,
    }


def portal_shell(request):
    """Etiquetas y URLs del menú lateral en todo el portal autenticado."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    role = getattr(user, "role", Student.Role.STUDENT)
    if user.is_superuser:
        role = Student.Role.ADMIN
    home_url = reverse(user.get_dashboard_url_name())
    return {
        "student": user,
        "portal_role_label": _ROLE_LABELS.get(role, "Usuario"),
        "portal_home_url": home_url,
    }
