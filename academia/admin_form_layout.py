"""Secciones y anchos de campos para formularios de creación en el portal admin."""

from academia.forms import (
    AcademicPeriodAdminCreateForm,
    EnrollmentAdminCreateForm,
    OfferingAdminCreateForm,
    ProgramAdminCreateForm,
    StudentAdminCreateForm,
)

FIELD_WIDTH = {
    "username": "full",
    "email": "full",
    "name": "full",
    "password1": "full",
    "password2": "full",
    "student": "full",
    "offering": "full",
    "teacher": "full",
    "is_active": "full",
    "is_current": "full",
    "academic_semester": "full",
    "code": "half",
    "semester": "half",
    "group": "half",
    "credits": "half",
    "starts_on": "half",
    "ends_on": "half",
    "status": "full",
    "role": "half",
    "academic_program": "half",
    "program": "half",
    "period": "half",
    "first_name": "half",
    "last_name": "half",
}

ADMIN_FORM_SECTIONS = {
    StudentAdminCreateForm: [
        {"title": "Identidad de acceso", "fields": ["username"]},
        {"title": "Datos personales", "fields": ["first_name", "last_name", "email"]},
        {
            "title": "Rol y programa",
            "fields": ["role", "academic_program", "academic_semester", "is_active"],
        },
        {"title": "Contraseña", "fields": ["password1", "password2"]},
    ],
    ProgramAdminCreateForm: [
        {"title": "Programa académico", "fields": ["name", "code"]},
    ],
    AcademicPeriodAdminCreateForm: [
        {"title": "Calendario lectivo", "fields": ["name", "starts_on", "ends_on", "is_current"]},
    ],
    OfferingAdminCreateForm: [
        {"title": "Carrera y período", "fields": ["program", "period"]},
        {"title": "Detalle del curso", "fields": ["name", "code", "semester", "group", "credits"]},
        {"title": "Docente", "fields": ["teacher"]},
    ],
    EnrollmentAdminCreateForm: [
        {"title": "Inscripción", "fields": ["student", "offering", "status"]},
    ],
}

COMPACT_FORMS = (
    ProgramAdminCreateForm,
    AcademicPeriodAdminCreateForm,
    EnrollmentAdminCreateForm,
)


def admin_form_layout_context(form):
    """Contexto de plantilla: secciones con campos bound y anchos."""
    layout = ADMIN_FORM_SECTIONS.get(
        type(form),
        [{"title": "Información", "fields": list(form.fields.keys())}],
    )
    sections = []
    for block in layout:
        fields = []
        for name in block["fields"]:
            if name not in form.fields:
                continue
            fields.append(
                {
                    "name": name,
                    "field": form[name],
                    "width": FIELD_WIDTH.get(name, "half"),
                }
            )
        if fields:
            sections.append({"title": block["title"], "fields": fields})
    return {
        "admin_form_sections": sections,
        "admin_form_compact": type(form) in COMPACT_FORMS,
    }
