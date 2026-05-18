# django_pkms/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from accounts.views import design_system


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("design-system/", design_system, name="design_system"),
    path("aula/", include("classroom.urls")),
    path("", include("notes.urls")),
    path(
        "",
        RedirectView.as_view(pattern_name="login", permanent=False),
        name="home",
    ),
    path("glossary/", include("glossary.urls")),
    path("revision/", include("revision.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
