"""Contexto del portal administrador (vistas con hash + datos reales)."""

from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from academia.models import AcademicPeriod, Enrollment, Offering, Program
from accounts.models import Student


def build_admin_alerts():
    alerts = []
    offerings_no_teacher = Offering.objects.filter(teacher__isnull=True).count()
    if offerings_no_teacher:
        alerts.append(
            {
                "level": "warn",
                "text": f"{offerings_no_teacher} curso(s) ofertado(s) sin docente asignado.",
                "goto": "ofertas",
                "preset_teacher": "missing",
            }
        )
    if not AcademicPeriod.objects.filter(is_current=True).exists():
        alerts.append(
            {
                "level": "warn",
                "text": "No hay período marcado como actual. Marque uno en Períodos.",
                "goto": "periodos",
            }
        )
    students_no_program = Student.objects.filter(
        role=Student.Role.STUDENT,
        academic_program__isnull=True,
    ).count()
    if students_no_program:
        alerts.append(
            {
                "level": "warn",
                "text": f"{students_no_program} estudiante(s) sin carrera asignada.",
                "url_name": "admin:accounts_student_changelist",
                "url_query": "?role__exact=student&academic_program__isnull=True",
            }
        )
    if not alerts:
        alerts.append(
            {
                "level": "ok",
                "text": "Sin alertas críticas en la configuración actual.",
                "url_name": None,
                "url_query": "",
            }
        )
    return alerts


def build_admin_portal_context():
    User = get_user_model()
    current_period = AcademicPeriod.objects.filter(is_current=True).first()
    program_count = Program.objects.count()
    period_count = AcademicPeriod.objects.count()
    offering_count = Offering.objects.count()
    active_enrollment_count = Enrollment.objects.filter(
        status=Enrollment.Status.ACTIVE
    ).count()

    admin_users = list(
        User.objects.select_related("academic_program")
        .order_by("-date_joined")[:200]
    )
    admin_programs = list(
        Program.objects.annotate(
            offering_count=Count("offerings"),
            student_count=Count("students"),
        ).order_by("name")
    )
    admin_periods = list(AcademicPeriod.objects.order_by("-name"))
    admin_offerings = list(
        Offering.objects.select_related("program", "period", "teacher")
        .annotate(
            active_student_count=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
            ),
        )
        .order_by("-period__name", "program__name", "code")
    )
    admin_enrollments = list(
        Enrollment.objects.select_related(
            "student",
            "offering",
            "offering__program",
            "offering__period",
            "offering__teacher",
        ).order_by("-enrolled_at")[:300]
    )

    program_choices = list(Program.objects.order_by("name").values("id", "name", "code"))
    period_choices = list(AcademicPeriod.objects.order_by("-name").values("id", "name", "is_current"))

    return {
        "current_period": current_period,
        "period_label": current_period.name if current_period else "Sin período actual",
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "teacher_count": User.objects.filter(role=Student.Role.TEACHER).count(),
        "student_role_count": User.objects.filter(role=Student.Role.STUDENT).count(),
        "admin_count": User.objects.filter(role=Student.Role.ADMIN).count(),
        "program_count": program_count,
        "period_count": period_count,
        "offering_count": offering_count,
        "active_enrollment_count": active_enrollment_count,
        "withdrawn_enrollment_count": Enrollment.objects.filter(
            status=Enrollment.Status.WITHDRAWN
        ).count(),
        "offerings_without_teacher": Offering.objects.filter(teacher__isnull=True).count(),
        "students_missing_program_count": User.objects.filter(
            role=Student.Role.STUDENT,
            academic_program__isnull=True,
        ).count(),
        "admin_users": admin_users,
        "admin_programs": admin_programs,
        "admin_periods": admin_periods,
        "admin_offerings": admin_offerings,
        "admin_enrollments": admin_enrollments,
        "admin_alerts": build_admin_alerts(),
        "admin_program_choices": program_choices,
        "admin_period_choices": period_choices,
        "admin_role_choices": [
            {"value": "", "label": "Todos los roles"},
            {"value": Student.Role.STUDENT, "label": "Estudiante"},
            {"value": Student.Role.TEACHER, "label": "Docente"},
            {"value": Student.Role.ADMIN, "label": "Administrador"},
        ],
        "admin_enrollment_status_choices": [
            {"value": "", "label": "Todos los estados"},
            {"value": Enrollment.Status.ACTIVE, "label": "Activa"},
            {"value": Enrollment.Status.WITHDRAWN, "label": "Baja"},
        ],
        "recent_periods": admin_periods[:12],
        "recent_users": admin_users[:10],
        "recent_offerings": admin_offerings[:12],
        "recent_enrollments": [
            e for e in admin_enrollments if e.status == Enrollment.Status.ACTIVE
        ][:12],
    }
