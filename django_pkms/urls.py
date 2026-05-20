# django_pkms/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from accounts.views import design_system, login
from accounts.site_views import (
    site_contacto,
    site_estrategia,
    site_home,
    site_innovacion,
    site_nosotros,
    site_producto,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("design-system/", design_system, name="design_system"),
    path("aula/", include("classroom.urls")),
    path("", login, name="login"),
    path("home/", site_home, name="site_home"),
    path("nosotros/", site_nosotros, name="site_nosotros"),
    path("estrategia/", site_estrategia, name="site_estrategia"),
    path("producto/", site_producto, name="site_producto"),
    path("innovacion/", site_innovacion, name="site_innovacion"),
    path("contacto/", site_contacto, name="site_contacto"),
    path("", include("notes.urls")),
    path("glossary/", include("glossary.urls")),
    path("revision/", include("revision.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
