# accounts/urls.py
from django.urls import path, include
from django.views.generic import RedirectView
from .views import *
from django.contrib.auth import urls as auth_urls


urlpatterns = [
    path("login/", login, name="login"),
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
    path("profile/<int:user_id>/<username>/", profile, name="profile"),
    path("delete/", delete_account, name="delete_account"),
    path("", include(auth_urls)),
]
