"""Contexto del aula para plantillas del portal estudiante."""

from django.db.models import Avg, Prefetch
from django.utils import timezone

from academia.models import Enrollment
from classroom.models import (
    AcademicWeek,
    Activity,
    Announcement,
    Grade,
    StudyMaterial,
    Submission,
)
from classroom.access import get_offering_for_student


def _submission_stats_for_offering(student, offering):
    activities = Activity.objects.filter(
        week__offering=offering,
        status=Activity.Status.PUBLISHED,
    )
    total = activities.count()
    submissions = Submission.objects.filter(
        student=student,
        activity__week__offering=offering,
        is_draft=False,
    ).exclude(status=Submission.Status.DRAFT)
    submitted_count = submissions.count()
    graded = Grade.objects.filter(
        submission__student=student,
        submission__activity__week__offering=offering,
    )
    avg = graded.aggregate(avg=Avg("score"))["avg"]
    return {
        "activities_total": total,
        "submissions_count": submitted_count,
        "average_score": avg,
        "graded_count": graded.count(),
    }


def _annotate_week_activities(week_activities, student):
    for act in week_activities:
        subs = getattr(act, "student_submissions", [])
        act.student_submission = subs[0] if subs else None


def build_course_page_context(student, offering):
    from classroom.portal import build_course_extras

    classroom_weeks = list(
        AcademicWeek.objects.filter(offering=offering).order_by("week_number")
    )
    return {
        "current_offering": offering,
        "classroom_weeks": classroom_weeks,
        "course_announcements": list(
            Announcement.objects.filter(offering=offering).order_by("-published_at")[:8]
        ),
        "course_stats": _submission_stats_for_offering(student, offering),
        **build_course_extras(student, offering),
    }


def build_week_page_context(student, week):
    from classroom.portal import (
        build_week_navigation,
        describe_activity_status,
        resolve_student_activity_action,
    )

    week_materials = list(StudyMaterial.objects.filter(week=week).order_by("title"))
    week_activities = list(
        Activity.objects.filter(week=week, status=Activity.Status.PUBLISHED)
        .order_by("due_at", "title")
        .prefetch_related(
            Prefetch(
                "submissions",
                queryset=Submission.objects.filter(student=student),
                to_attr="student_submissions",
            )
        )
    )
    _annotate_week_activities(week_activities, student)
    for act in week_activities:
        sub = act.student_submission
        act.status_meta = describe_activity_status(act, sub)
        act.type_label = student_activity_type_label(act)
        act.action = resolve_student_activity_action(
            act.id, act.status_meta["state"], act.activity_type
        )
    prev_n, next_n = build_week_navigation(week.offering, week.week_number)
    return {
        "current_offering": week.offering,
        "current_week": week,
        "week_materials": week_materials,
        "week_activities": week_activities,
        "week_prev_number": prev_n,
        "week_next_number": next_n,
    }


def student_activity_type_label(activity):
    """Etiqueta visible para estudiantes (actividad, taller, etc.)."""
    return activity.get_activity_type_display()


def _activity_submit_success_message(display, activity_type):
    """Concordancia entregada/entregado según el tipo."""
    masculine = {
        Activity.ActivityType.WORKSHOP,
        Activity.ActivityType.QUIZ,
        Activity.ActivityType.EXAM,
        Activity.ActivityType.FORUM,
    }
    if activity_type in masculine:
        return f"{display} entregado correctamente."
    return f"{display} entregada correctamente."


def build_activity_labels(activity):
    """Textos de entrega según Activity.activity_type (lo que eligió el docente)."""
    display = student_activity_type_label(activity)
    dl = display.lower()
    at = activity.activity_type

    base = {
        "type_name": display,
        "type_name_lower": dl,
        "requires_file": True,
    }

    if at == Activity.ActivityType.FORUM:
        return {
            **base,
            "requires_file": False,
            "delivery_heading": "Tu participación",
            "submit_button": "Publicar en el foro",
            "draft_button": "Guardar borrador",
            "file_label": "Adjunto (opcional)",
            "comment_label": "Mensaje",
            "comment_placeholder": "Escribe tu respuesta al foro…",
            "checklist_legend": "Antes de publicar",
            "check_instructions": "Leí el tema y las instrucciones del foro",
            "check_format": "Mi mensaje o adjunto cumple formato y tamaño (máx. 10 MB)",
            "check_confirm": "Confirmo que mi respuesta está lista para publicar",
            "file_hint": "PDF, Word, imágenes, ZIP u Office. Máximo 10 MB. Opcional en foros.",
            "upload_prompt": "Arrastra un archivo o haz clic para adjuntarlo (opcional)",
            "upload_empty": "Sin archivo adjunto — puedes publicar solo con tu mensaje",
            "submit_success": "Respuesta publicada correctamente.",
            "submit_error_empty": "Escribe un mensaje o adjunta un archivo para publicar.",
            "submit_error_checklist": "Marca el checklist de verificación antes de publicar.",
        }

    if at == Activity.ActivityType.DELIVERY:
        delivery_heading = "Tu envío"
        submit_button = "Enviar entrega"
    else:
        delivery_heading = f"Tu {dl}"
        submit_button = f"Entregar {dl}"

    return {
        **base,
        "delivery_heading": delivery_heading,
        "submit_button": submit_button,
        "draft_button": "Guardar borrador",
        "file_label": f"Archivo · {display}",
        "comment_label": "Comentario (opcional)",
        "comment_placeholder": f"Nota para el docente sobre tu {dl}…",
        "checklist_legend": f"Antes de entregar tu {dl}",
        "check_instructions": "Leí las instrucciones",
        "check_format": "El archivo cumple formato y tamaño (máx. 10 MB)",
        "check_confirm": f"Confirmo que mi {dl} está lista para entregar",
        "file_hint": "PDF, Word, imágenes, ZIP u Office. Máximo 10 MB.",
        "upload_prompt": "Arrastra tu archivo aquí o haz clic para seleccionarlo",
        "upload_empty": "Ningún archivo seleccionado",
        "submit_success": _activity_submit_success_message(display, at),
        "submit_error_empty": f"Adjunta un archivo para entregar tu {dl}.",
        "submit_error_checklist": "Marca el checklist de verificación antes de entregar.",
    }


def build_activity_page_context(student, activity):
    from classroom.portal import describe_activity_status

    submission, _ = Submission.objects.get_or_create(
        activity=activity,
        student=student,
        defaults={"is_draft": True, "status": Submission.Status.DRAFT},
    )
    return {
        "current_offering": activity.week.offering,
        "current_week": activity.week,
        "current_activity": activity,
        "current_submission": submission,
        "activity_status": describe_activity_status(activity, submission),
        "activity_labels": build_activity_labels(activity),
    }


def _enrollment_card_status_label(current_week, progress_pct):
    if current_week:
        if current_week.status == AcademicWeek.Status.IN_PROGRESS:
            return f"En curso · Semana {current_week.week_number}"
        if current_week.status == AcademicWeek.Status.COMPLETED:
            return f"Completada · Semana {current_week.week_number}"
        if current_week.status == AcademicWeek.Status.LOCKED:
            return "Bloqueada"
        return f"Semana {current_week.week_number}"
    if progress_pct >= 100:
        return "Completado"
    return "En curso"


def build_enrollment_cards(student):
    """Tarjetas de curso institucional con avance y semana actual."""
    enrollments = (
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
        .select_related(
            "offering",
            "offering__program",
            "offering__teacher",
            "offering__period",
        )
        .order_by("-offering__period__name", "offering__code")
    )
    cards = []
    featured_set = False
    for enr in enrollments:
        off = enr.offering
        weeks = list(AcademicWeek.objects.filter(offering=off).order_by("week_number"))
        current_week = next(
            (w for w in weeks if w.status == AcademicWeek.Status.IN_PROGRESS),
            None,
        )
        if not current_week and weeks:
            completed = [w for w in weeks if w.status == AcademicWeek.Status.COMPLETED]
            if len(completed) < len(weeks):
                idx = len(completed)
                current_week = weeks[idx] if idx < len(weeks) else weeks[-1]
        total_weeks = len(weeks) or 1
        done_weeks = sum(1 for w in weeks if w.status == AcademicWeek.Status.COMPLETED)
        progress_pct = round(100 * done_weeks / total_weeks) if weeks else 0
        is_featured = False
        if not featured_set and current_week and current_week.status == AcademicWeek.Status.IN_PROGRESS:
            is_featured = True
            featured_set = True
        cards.append(
            {
                "enrollment": enr,
                "offering": off,
                "current_week": current_week,
                "progress_pct": progress_pct,
                "status_label": _enrollment_card_status_label(current_week, progress_pct),
                "is_featured": is_featured,
                "stats": _submission_stats_for_offering(student, off),
            }
        )
    if cards and not featured_set:
        cards[0]["is_featured"] = True
    return cards


def build_enrollment_list_context(student):
    cards = build_enrollment_cards(student)
    period_label = cards[0]["offering"].period.name if cards else ""
    return {
        "enrollment_cards": cards,
        "catalog_period_label": period_label,
    }


def _active_offering_ids(student):
    return Enrollment.objects.filter(
        student=student,
        status=Enrollment.Status.ACTIVE,
    ).values_list("offering_id", flat=True)


def _avg_scores_for_week_ids(student, week_ids):
    if not week_ids:
        return None
    avg = (
        Grade.objects.filter(
            submission__student=student,
            submission__activity__week_id__in=week_ids,
        ).aggregate(a=Avg("score"))["a"]
    )
    return round(float(avg), 1) if avg is not None else None


def _period_bucket_scores(student, offering):
    """Promedios de los 3 cortes (P1/P2/P3) por tercios de semanas del curso."""
    weeks = list(
        AcademicWeek.objects.filter(offering=offering).order_by("week_number")
    )
    if not weeks:
        return None, None, None
    size = max(1, (len(weeks) + 2) // 3)
    w1 = [w.id for w in weeks[:size]]
    w2 = [w.id for w in weeks[size : size * 2]]
    w3 = [w.id for w in weeks[size * 2 :]]
    return (
        _avg_scores_for_week_ids(student, w1),
        _avg_scores_for_week_ids(student, w2),
        _avg_scores_for_week_ids(student, w3),
    )


def _acumulado_parcial(p1, p2, p3):
    """Nota acumulada: promedio ponderado solo de cortes ya calificados (30/30/40)."""
    parts = []
    if p1 is not None:
        parts.append((p1, 0.3))
    if p2 is not None:
        parts.append((p2, 0.3))
    if p3 is not None:
        parts.append((p3, 0.4))
    if not parts:
        return None
    total_w = sum(weight for _, weight in parts)
    return round(sum(val * weight for val, weight in parts) / total_w, 2)


def _definitiva_final(p1, p2, p3):
    """Definitiva solo cuando hay nota del corte 3 (P3 / 40%)."""
    if p3 is None:
        return None
    parts = []
    if p1 is not None:
        parts.append((p1, 0.3))
    if p2 is not None:
        parts.append((p2, 0.3))
    parts.append((p3, 0.4))
    total_w = sum(weight for _, weight in parts)
    return round(sum(val * weight for val, weight in parts) / total_w, 2)


def _format_score_display(value):
    if value is None:
        return None
    rounded = round(float(value), 2)
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    return text


def build_course_grade_summary_rows(student, enrollments):
    rows = []
    for enr in enrollments:
        off = enr.offering
        p1, p2, p3 = _period_bucket_scores(student, off)
        acum = _acumulado_parcial(p1, p2, p3)
        final = _definitiva_final(p1, p2, p3)
        rows.append(
            {
                "offering": off,
                "group": off.group,
                "name": off.name,
                "semester": off.semester,
                "credits": off.credits,
                "search": f"{off.group} {off.code} {off.name}".lower(),
                "p1": p1,
                "p2": p2,
                "p3": p3,
                "p1_display": _format_score_display(p1),
                "p2_display": _format_score_display(p2),
                "p3_display": _format_score_display(p3),
                "acumulado": acum,
                "acumulado_display": _format_score_display(acum),
                "final": final,
                "final_display": _format_score_display(final),
            }
        )
    return rows


def build_activity_grade_detail_rows(student):
    """Todas las actividades publicadas: calificadas y pendientes."""
    offering_ids = list(_active_offering_ids(student))
    if not offering_ids:
        return []

    activities = (
        Activity.objects.filter(
            week__offering_id__in=offering_ids,
            status=Activity.Status.PUBLISHED,
        )
        .select_related("week", "week__offering")
        .order_by("-due_at", "title")
    )
    rows = []
    now = timezone.now()
    for act in activities:
        sub = (
            Submission.objects.filter(activity=act, student=student)
            .select_related()
            .first()
        )
        grade = Grade.objects.filter(submission=sub).first() if sub else None
        if grade:
            status_label = "Calificado"
            status_class = "ok"
            score_display = _format_score_display(grade.score)
            feedback = (grade.feedback or "").strip() or "—"
        elif sub and not sub.is_draft:
            status_label = "Pendiente"
            status_class = "pending"
            score_display = None
            feedback = "—"
        elif act.due_at and act.due_at < now and (not sub or sub.is_draft):
            status_label = "Pendiente - no entregado"
            status_class = "pending-missing"
            score_display = None
            feedback = "—"
        else:
            status_label = "Pendiente"
            status_class = "pending"
            score_display = None
            feedback = "—"

        delivery_date = act.due_at
        rows.append(
            {
                "activity": act,
                "offering": act.week.offering,
                "status_label": status_label,
                "status_class": status_class,
                "score_display": score_display,
                "feedback": feedback,
                "delivery_date": delivery_date,
                "search": f"{act.title} {act.week.offering.code}".lower(),
            }
        )
    return rows


def build_grades_context(student):
    """Calificaciones institucionales (resumen por curso y detalle por actividad)."""
    enrollments = (
        Enrollment.objects.filter(
            student=student,
            status=Enrollment.Status.ACTIVE,
        )
        .select_related("offering", "offering__period", "offering__teacher")
        .order_by("-offering__period__name", "offering__code")
    )

    course_grade_rows = build_course_grade_summary_rows(student, enrollments)
    activity_grade_detail_rows = build_activity_grade_detail_rows(student)

    offering_ids = list(_active_offering_ids(student))
    published_activities = Activity.objects.filter(
        week__offering_id__in=offering_ids,
        status=Activity.Status.PUBLISHED,
    )
    pending_activity_count = 0
    for act in published_activities:
        sub = Submission.objects.filter(activity=act, student=student).first()
        if sub and Grade.objects.filter(submission=sub).exists():
            continue
        pending_activity_count += 1

    all_graded = Grade.objects.filter(submission__student=student)
    overall_avg = all_graded.aggregate(avg=Avg("score"))["avg"]
    overall_avg_display = (
        _format_score_display(overall_avg) if overall_avg is not None else None
    )

    grades_period_label = ""
    if enrollments:
        grades_period_label = enrollments[0].offering.period.name

    enrollment_grade_rows = []
    for enr in enrollments:
        enrollment_grade_rows.append({"offering": enr.offering, "average": None})

    return {
        "course_grade_rows": course_grade_rows,
        "standard_course_grade_rows": course_grade_rows,
        "activity_grade_detail_rows": activity_grade_detail_rows,
        "enrollment_grade_rows": enrollment_grade_rows,
        "grades_period_label": grades_period_label,
        "pending_activity_count": pending_activity_count,
        "overall_avg_display": overall_avg_display,
        "graded_activity_count": all_graded.count(),
    }


def build_teacher_submissions_context(teacher):
    """Entregas de cursos que imparte el docente."""
    base = Submission.objects.filter(
        activity__week__offering__teacher=teacher,
        is_draft=False,
    ).exclude(status=Submission.Status.DRAFT)

    pending = list(
        base.filter(grade__isnull=True)
        .select_related(
            "student",
            "activity",
            "activity__week",
            "activity__week__offering",
        )
        .order_by("activity__due_at", "-submitted_at")[:50]
    )

    graded_count = base.filter(grade__isnull=False).count()
    pending_count = len(pending)

    return {
        "teacher_pending_submissions": pending,
        "teacher_pending_submission_count": pending_count,
        "teacher_graded_submission_count": graded_count,
    }


