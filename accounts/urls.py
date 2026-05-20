# accounts/urls.py
from django.urls import path, include
from django.views.generic import RedirectView
from .views import *
from django.contrib.auth import urls as auth_urls


def _auth_urlpatterns():
    skip = {"password_change", "password_change_done"}
    return [p for p in auth_urls.urlpatterns if getattr(p, "name", None) not in skip]


urlpatterns = [
    path("login/", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("panel/docente/", dashboard_teacher, name="dashboard_teacher"),
    path("panel/administrador/", dashboard_admin, name="dashboard_admin"),
    path(
        "signup/",
        RedirectView.as_view(pattern_name="login", permanent=False),
        name="signup",
    ),
    # profile urls
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("notifications/read/", notifications_mark_read, name="notifications_mark_read"),
    path("profile/", profile, name="profile"),
    path("profile/<int:user_id>/<username>/", profile, name="profile_detail"),
    path("delete/", delete_account, name="delete_account"),
    path(
        "password/change/",
        PortalPasswordChangeView.as_view(),
        name="password_change",
    ),
] + _auth_urlpatterns()
