"""Sitio público · Proyecto final (presencia digital EasyLearn)."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from accounts.forms import SiteContactForm, SiteLeadForm


def _ctx(active_nav, **extra):
    return {"sitio_nav": active_nav, **extra}


@require_http_methods(["GET", "POST"])
def site_home(request):
    lead_form = SiteLeadForm()
    if request.method == "POST":
        lead_form = SiteLeadForm(request.POST)
        if lead_form.is_valid():
            messages.success(
                request,
                "¡Gracias! Recibimos tu correo. Te contactaremos pronto con más información "
                "(simulación de envío).",
            )
            return redirect(reverse("site_home") + "#contacto-home")
    return render(
        request,
        "easylearn/sitio/home.html",
        _ctx("home", lead_form=lead_form),
    )


@require_http_methods(["GET"])
def site_nosotros(request):
    return render(request, "easylearn/sitio/nosotros.html", _ctx("nosotros"))


@require_http_methods(["GET"])
def site_estrategia(request):
    return render(request, "easylearn/sitio/estrategia.html", _ctx("estrategia"))


@require_http_methods(["GET"])
def site_producto(request):
    return render(request, "easylearn/sitio/producto.html", _ctx("courses"))


@require_http_methods(["GET"])
def site_innovacion(request):
    return render(request, "easylearn/sitio/innovacion.html", _ctx("blog"))


@require_http_methods(["GET", "POST"])
def site_contacto(request):
    form = SiteContactForm()
    enviado = False
    if request.method == "POST":
        form = SiteContactForm(request.POST)
        if form.is_valid():
            enviado = True
            messages.success(
                request,
                "¡Mensaje recibido! Nuestro equipo de EasyLearn responderá en un plazo "
                "de 24 a 48 horas hábiles (simulación de envío).",
            )
            return redirect("site_contacto")
    return render(
        request,
        "easylearn/sitio/contacto.html",
        _ctx("contacto", form=form, enviado=enviado),
    )
