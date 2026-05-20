"""Vistas de creación en el portal administrador (sin Django Admin)."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.decorators import role_required
from accounts.models import Profile, Student

from academia.admin_form_layout import admin_form_layout_context
from academia.forms import (
    AcademicPeriodAdminCreateForm,
    EnrollmentAdminCreateForm,
    OfferingAdminCreateForm,
    ProgramAdminCreateForm,
    StudentAdminCreateForm,
)


def _admin_form_page_context(request, *, kicker, title, description, cancel_hash):
    Profile.objects.get_or_create(student=request.user)
    return {
        "student": request.user,
        "portal_role_label": "Administrador",
        "user": request.user,
        "header_search_action": reverse("dashboard_admin"),
        "header_search_placeholder": "Buscar usuarios, cursos, roles…",
        "header_search_label": "Filtrar tablero administrador",
        "admin_form_kicker": kicker,
        "admin_form_title": title,
        "admin_form_description": description,
        "admin_form_cancel_url": f"{reverse('dashboard_admin')}#{cancel_hash}",
        "admin_form_cancel_label": "Volver al listado",
    }


def _handle_create(request, *, form_class, success_message, cancel_hash, page_context):
    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(f"{reverse('dashboard_admin')}#{cancel_hash}")
    return render(
        request,
        "easylearn/portal_admin_create.html",
        {**page_context, "form": form, **admin_form_layout_context(form)},
    )


@login_required
@role_required(Student.Role.ADMIN)
def admin_create_user(request):
    return _handle_create(
        request,
        form_class=StudentAdminCreateForm,
        success_message="Usuario creado correctamente.",
        cancel_hash="usuarios",
        page_context=_admin_form_page_context(
            request,
            kicker="Usuarios",
            title="Crear usuario",
            description="Registre una cuenta con rol, carrera opcional y acceso al portal.",
            cancel_hash="usuarios",
        ),
    )


@login_required
@role_required(Student.Role.ADMIN)
def admin_create_program(request):
    return _handle_create(
        request,
        form_class=ProgramAdminCreateForm,
        success_message="Carrera creada correctamente.",
        cancel_hash="carreras",
        page_context=_admin_form_page_context(
            request,
            kicker="Carreras",
            title="Crear carrera",
            description="Defina el nombre y código del programa académico. El identificador URL se genera automáticamente.",
            cancel_hash="carreras",
        ),
    )


@login_required
@role_required(Student.Role.ADMIN)
def admin_create_period(request):
    return _handle_create(
        request,
        form_class=AcademicPeriodAdminCreateForm,
        success_message="Período académico creado correctamente.",
        cancel_hash="periodos",
        page_context=_admin_form_page_context(
            request,
            kicker="Períodos",
            title="Crear período",
            description="Configure el calendario lectivo. Si marca «Período actual», los demás se desactivan automáticamente.",
            cancel_hash="periodos",
        ),
    )


@login_required
@role_required(Student.Role.ADMIN)
def admin_create_offering(request):
    return _handle_create(
        request,
        form_class=OfferingAdminCreateForm,
        success_message="Curso ofertado creado correctamente.",
        cancel_hash="ofertas",
        page_context=_admin_form_page_context(
            request,
            kicker="Cursos ofertados",
            title="Crear curso",
            description="Vincule carrera, período, grupo y docente responsable del curso.",
            cancel_hash="ofertas",
        ),
    )


@login_required
@role_required(Student.Role.ADMIN)
def admin_create_enrollment(request):
    return _handle_create(
        request,
        form_class=EnrollmentAdminCreateForm,
        success_message="Matrícula registrada correctamente.",
        cancel_hash="matriculas",
        page_context=_admin_form_page_context(
            request,
            kicker="Matrículas",
            title="Crear matrícula",
            description="Inscriba un estudiante en un curso ofertado del período vigente.",
            cancel_hash="matriculas",
        ),
    )
