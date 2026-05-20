"""Contexto del portal estudiante (Inicio, Mis cursos, Calendario, Mensajes)."""

import json
from calendar import monthrange
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from academia.models import Enrollment
from classroom.context import _submission_stats_for_offering, build_enrollment_cards
from classroom.models import AcademicWeek, Activity, Announcement, Grade, StudyMaterial, Submission


def resolve_student_activity_action(activity_id, state, activity_type=None):
    """
    Botón de acción según estado:
    pendiente → Entregar (verde); entregada → Ver entrega (azul);
    calificada → Ver calificación (verde); vencida → sin acción.
    """
    submit_url = reverse("classroom:activity_submit", args=[activity_id])
    if state == "overdue":
        return {
            "action_label": None,
            "action_url": None,
            "action_btn_class": None,
        }
    if activity_type == "forum":
        if state in ("graded", "submitted"):
            return {
                "action_label": "Ver calificación" if state == "graded" else "Ver entrega",
                "action_url": submit_url,
                "action_btn_class": (
                    "btn-portal-success" if state == "graded" else "btn-outline"
                ),
            }
        return {
            "action_label": "Participar",
            "action_url": submit_url,
            "action_btn_class": "btn-portal-success",
        }
    if state == "pending":
        return {
            "action_label": "Entregar",
            "action_url": submit_url,
            "action_btn_class": "btn-portal-success",
        }
    if state == "graded":
        return {
            "action_label": "Ver calificación",
            "action_url": submit_url,
            "action_btn_class": "btn-portal-success",
        }
    if state == "submitted":
        return {
            "action_label": "Ver entrega",
            "action_url": submit_url,
            "action_btn_class": "btn-outline",
        }
    return {
        "action_label": "Ver entrega",
        "action_url": submit_url,
        "action_btn_class": "btn-outline",
    }


def describe_activity_status(activity, submission=None):
    """Estado visual de una actividad para el estudiante."""
    now = timezone.now()
    if submission and getattr(submission, "grade", None):
        return {
            "status_label": "Calificada",
            "badge": "ok",
            "state": "graded",
            "is_overdue": False,
        }
    if submission and not submission.is_draft:
        return {
            "status_label": "Entregado",
            "badge": "ok",
            "state": "submitted",
            "is_overdue": False,
        }
    overdue = bool(
        activity.due_at
        and activity.due_at < now
        and not activity.allow_late
    )
    if overdue:
        return {
            "status_label": "Vencida",
            "badge": "danger",
            "state": "overdue",
            "is_overdue": True,
        }
    if activity.due_at:
        return {
            "status_label": "Pendiente",
            "badge": "warn",
            "state": "pending",
            "is_overdue": False,
        }
    return {
        "status_label": "Disponible",
        "badge": "draft",
        "state": "pending",
        "is_overdue": False,
    }


def _active_offering_ids(student):
    return Enrollment.objects.filter(
        student=student,
        status=Enrollment.Status.ACTIVE,
    ).values_list("offering_id", flat=True)


def build_dashboard_activities(student):
    """Actividades prioritarias (solo institucionales)."""
    offering_ids = list(_active_offering_ids(student))
    activities = (
        Activity.objects.filter(
            week__offering_id__in=offering_ids,
            status=Activity.Status.PUBLISHED,
        )
        .select_related("week", "week__offering")
        .order_by("due_at", "title")[:30]
    )
    rows = []
    for act in activities:
        sub = Submission.objects.filter(activity=act, student=student).first()
        meta = describe_activity_status(act, sub)
        if meta["state"] == "graded":
            continue
        rows.append(
            {
                "activity": act,
                "submission": sub,
                **meta,
                **resolve_student_activity_action(
                    act.id, meta["state"], act.activity_type
                ),
            }
        )
    rows.sort(
        key=lambda r: (
            0 if r["state"] == "overdue" else 1,
            r["activity"].due_at is None,
            r["activity"].due_at or timezone.now(),
        )
    )
    return rows[:10]


def _pending_activity_count(student):
    now = timezone.now()
    offering_ids = list(_active_offering_ids(student))
    count = 0
    activities = Activity.objects.filter(
        week__offering_id__in=offering_ids,
        status=Activity.Status.PUBLISHED,
    )
    for act in activities:
        sub = Submission.objects.filter(activity=act, student=student).first()
        meta = describe_activity_status(act, sub)
        if meta["state"] in ("pending", "overdue"):
            count += 1
    return count


def build_performance_bars(student):
    """Promedios por curso para la gráfica del inicio."""
    grades = Grade.objects.filter(submission__student=student).select_related(
        "submission__activity__week__offering"
    )
    buckets = {}
    for g in grades:
        off = g.submission.activity.week.offering
        buckets.setdefault(off.id, {"offering": off, "scores": []})
        buckets[off.id]["scores"].append(float(g.score))
    bars = []
    for item in buckets.values():
        scores = item["scores"]
        avg = sum(scores) / len(scores) if scores else None
        if avg is None:
            continue
        bars.append(
            {
                "offering": item["offering"],
                "average": round(avg, 1),
                "bar_pct": min(100, round(avg / 5.0 * 100)),
            }
        )
    bars.sort(key=lambda b: b["offering"].code)
    return bars


def build_upcoming_evaluations(student, limit=5):
    now = timezone.now()
    offering_ids = list(_active_offering_ids(student))
    acts = (
        Activity.objects.filter(
            week__offering_id__in=offering_ids,
            status=Activity.Status.PUBLISHED,
            due_at__gte=now,
        )
        .select_related("week", "week__offering")
        .order_by("due_at")[:limit]
    )
    items = []
    for act in acts:
        sub = Submission.objects.filter(activity=act, student=student).first()
        if sub and getattr(sub, "grade", None):
            continue
        items.append(
            {
                "activity": act,
                "due_at": act.due_at,
                "url": reverse("classroom:activity_submit", args=[act.id]),
            }
        )
    return items


def build_mini_calendar(student):
    """Días del mes actual con entregas programadas."""
    now = timezone.localtime()
    year, month = now.year, now.month
    _, days_in_month = monthrange(year, month)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(day=days_in_month, hour=23, minute=59, second=59)
    offering_ids = list(_active_offering_ids(student))
    due_days = set()
    for act in Activity.objects.filter(
        week__offering_id__in=offering_ids,
        status=Activity.Status.PUBLISHED,
        due_at__gte=start,
        due_at__lte=end,
    ):
        local = timezone.localtime(act.due_at)
        due_days.add(local.day)
    month_names = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]
    return {
        "calendar_year": year,
        "calendar_month": month,
        "calendar_month_label": f"{month_names[month - 1]} {year}",
        "calendar_due_days_json": json.dumps(sorted(due_days)),
        "calendar_today": now.day,
    }


def build_next_class_hint(student):
    """Próxima fecha relevante: entrega o inicio de semana."""
    now = timezone.now()
    offering_ids = list(_active_offering_ids(student))
    nxt = (
        Activity.objects.filter(
            week__offering_id__in=offering_ids,
            status=Activity.Status.PUBLISHED,
            due_at__gte=now,
        )
        .select_related("week__offering")
        .order_by("due_at")
        .first()
    )
    if nxt:
        return {
            "label": nxt.title[:48],
            "sub": f"{nxt.week.offering.code} · entrega {timezone.localtime(nxt.due_at).strftime('%d %b, %H:%M').lstrip('0')}",
            "url": reverse("classroom:activity_submit", args=[nxt.id]),
        }
    week = (
        AcademicWeek.objects.filter(
            offering_id__in=offering_ids,
            starts_on__gte=now.date(),
        )
        .select_related("offering")
        .order_by("starts_on")
        .first()
    )
    if week and week.starts_on:
        return {
            "label": f"Semana {week.week_number}",
            "sub": f"{week.offering.code} · {week.title[:40]}",
            "url": reverse(
                "classroom:week_detail",
                kwargs={"offering_id": week.offering_id, "week_number": week.week_number},
            ),
        }
    return None


def build_academic_calendar_events(student):
    """Entregas con fecha límite para calendario mensual + tabla del portal."""
    now = timezone.now()
    offering_ids = list(_active_offering_ids(student))
    range_start = now - timedelta(days=60)
    range_end = now + timedelta(days=365)
    events = []
    for act in (
        Activity.objects.filter(
            week__offering_id__in=offering_ids,
            status=Activity.Status.PUBLISHED,
            due_at__gte=range_start,
            due_at__lte=range_end,
        )
        .exclude(due_at__isnull=True)
        .select_related("week", "week__offering")
        .order_by("due_at")
    ):
        local = timezone.localtime(act.due_at)
        week = act.week
        meta = describe_activity_status(
            act, Submission.objects.filter(activity=act, student=student).first()
        )
        action = resolve_student_activity_action(
            act.id, meta["state"], act.activity_type
        )
        events.append(
            {
                "date": local.date(),
                "date_iso": local.date().isoformat(),
                "year": local.year,
                "month": local.month,
                "day": local.day,
                "time_label": local.strftime("%H:%M"),
                "title": act.title,
                "offering_code": act.week.offering.code,
                "offering_name": act.week.offering.name,
                "type": "entrega",
                "status_label": meta["status_label"],
                "badge": meta["badge"],
                "state": meta["state"],
                "week_url": reverse(
                    "classroom:week_detail",
                    kwargs={
                        "offering_id": week.offering_id,
                        "week_number": week.week_number,
                    },
                ),
                "submit_url": action["action_url"],
                "search": (
                    f"{act.title} {act.week.offering.code} {meta['status_label']}"
                ).lower(),
                **action,
            }
        )
    return events


def build_academic_calendar_events_payload(events):
    """Payload compacto para el calendario mensual (json_script en plantilla)."""
    return [
        {
            "date": ev["date_iso"],
            "year": ev["year"],
            "month": ev["month"],
            "day": ev["day"],
            "badge": ev["badge"],
            "state": ev["state"],
        }
        for ev in events
    ]


def _format_reminder_when(due_at, is_today):
    local = timezone.localtime(due_at)
    if is_today:
        return f"Hoy · {local.strftime('%H:%M')}"
    return local.strftime("%d %b · %H:%M")


def build_course_schedule_slots(offering):
    """Horario de clase en ficha del curso (referencia demo hasta modelo de horarios)."""
    room = "Aula 402 · Presencial" if offering.group in ("A", "1", "") else f"Grupo {offering.group}"
    return [
        {
            "label": "Clase martes",
            "meta": room,
            "time": "7:40 a. m. – 9:20 a. m.",
            "alt": False,
        },
        {
            "label": "Clase jueves",
            "meta": "Laboratorio de software",
            "time": "7:40 a. m. – 9:20 a. m.",
            "alt": True,
        },
    ]


def build_course_extras(student, offering):
    """Recordatorios, horario y semana actual en panorama del curso."""
    today = timezone.localdate()
    due_today = []
    course_reminders = []

    published = Activity.objects.filter(
        week__offering=offering,
        status=Activity.Status.PUBLISHED,
    ).select_related("week").order_by("due_at")

    for act in published:
        sub = Submission.objects.filter(activity=act, student=student).first()
        meta = describe_activity_status(act, sub)
        if act.due_at and act.due_at.date() == today and meta["state"] in ("pending", "overdue"):
            due_today.append({"activity": act, **meta})
        if meta["state"] in ("pending", "overdue") and act.due_at:
            is_today = timezone.localtime(act.due_at).date() == today
            course_reminders.append(
                {
                    "activity": act,
                    "urgent": is_today,
                    "when_label": _format_reminder_when(act.due_at, is_today),
                    **meta,
                }
            )

    course_reminders.sort(key=lambda r: (not r["urgent"], r["activity"].due_at))
    course_reminders = course_reminders[:5]

    current_week = (
        AcademicWeek.objects.filter(offering=offering)
        .filter(status=AcademicWeek.Status.IN_PROGRESS)
        .order_by("week_number")
        .first()
    )
    if not current_week:
        current_week = (
            AcademicWeek.objects.filter(offering=offering)
            .exclude(status=AcademicWeek.Status.LOCKED)
            .order_by("-week_number")
            .first()
        )

    stats = _submission_stats_for_offering(student, offering)
    submissions_count = stats["submissions_count"]
    activities_total = stats["activities_total"] or 0
    entregas_hint = (
        f"Has entregado {submissions_count} de {activities_total} actividades"
        if activities_total
        else "Sin actividades publicadas"
    )

    return {
        "current_week_highlight": current_week,
        "course_due_today": due_today,
        "course_reminders": course_reminders,
        "course_schedule_slots": build_course_schedule_slots(offering),
        "course_entregas_hint": entregas_hint,
        "course_stats": stats,
    }


def build_week_navigation(offering, week_number):
    weeks = list(
        AcademicWeek.objects.filter(offering=offering).order_by("week_number").values_list(
            "week_number", flat=True
        )
    )
    if week_number not in weeks:
        return None, None
    idx = weeks.index(week_number)
    prev_n = weeks[idx - 1] if idx > 0 else None
    next_n = weeks[idx + 1] if idx < len(weeks) - 1 else None
    return prev_n, next_n


def build_repaso_personal_calendar_context(active_objectives, overdue_objectives):
    """Objetivos de repaso para la pestaña Calendario · Repaso personal."""
    today = timezone.localdate()
    overdue_list = list(overdue_objectives)
    active_list = list(active_objectives.order_by("end_date", "name"))
    rows = []
    events = []

    def _event_from_objective(obj, state, badge):
        return {
            "date": obj.end_date.isoformat(),
            "year": obj.end_date.year,
            "month": obj.end_date.month,
            "day": obj.end_date.day,
            "badge": badge,
            "state": state,
        }

    for obj in overdue_list:
        rows.append(
            {
                "objective": obj,
                "name": obj.name,
                "url": obj.get_absolute_url(),
                "end_date": obj.end_date,
                "end_date_iso": obj.end_date.isoformat(),
                "start_date": obj.start_date,
                "course_label": obj.course.name if obj.course_id else "General",
                "badge": "danger",
                "status_label": "Vencido",
                "state": "overdue",
                "days_label": f"Venció {obj.end_date.strftime('%d %b %Y')}",
                "search": f"{obj.name} vencido".lower(),
            }
        )
        events.append(_event_from_objective(obj, "overdue", "danger"))

    for obj in active_list:
        delta = (obj.end_date - today).days
        if delta <= 2:
            badge, state, status_label = "warn", "pending", "Urgente"
            days_label = "Vence hoy" if delta == 0 else f"Vence en {delta} día{'s' if delta != 1 else ''}"
        else:
            badge, state, status_label = "draft", "pending", "En curso"
            days_label = f"Hasta {obj.end_date.strftime('%d %b %Y')}"
        rows.append(
            {
                "objective": obj,
                "name": obj.name,
                "url": obj.get_absolute_url(),
                "end_date": obj.end_date,
                "end_date_iso": obj.end_date.isoformat(),
                "start_date": obj.start_date,
                "course_label": obj.course.name if obj.course_id else "General",
                "badge": badge,
                "status_label": status_label,
                "state": state,
                "days_label": days_label,
                "search": f"{obj.name} {status_label}".lower(),
            }
        )
        events.append(_event_from_objective(obj, state, badge))

    return {
        "repaso_cal_rows": rows,
        "repaso_cal_events_payload": events,
        "repaso_cal_active_count": len(active_list),
        "repaso_cal_overdue_count": len(overdue_list),
        "repaso_cal_total_count": len(active_list) + len(overdue_list),
    }


def build_repaso_materials(student):
    """Materiales de estudio publicados, agrupados por curso matriculado."""
    enrollments = (
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
        .select_related("offering", "offering__teacher", "offering__period", "offering__program")
        .order_by("-offering__period__name", "offering__code")
    )
    courses = []
    total_materials = 0
    for enr in enrollments:
        off = enr.offering
        weeks_data = []
        for week in AcademicWeek.objects.filter(offering=off).order_by("week_number"):
            materials = list(StudyMaterial.objects.filter(week=week).order_by("title"))
            if not materials:
                continue
            weeks_data.append({"week": week, "materials": materials})
            total_materials += len(materials)
        if not weeks_data:
            continue
        courses.append(
            {
                "offering": off,
                "weeks": weeks_data,
                "material_count": sum(len(w["materials"]) for w in weeks_data),
                "aula_url": reverse("classroom:course_detail", args=[off.id]),
                "week_count": len(weeks_data),
            }
        )
    return {
        "repaso_courses": courses,
        "repaso_material_total": total_materials,
        "repaso_course_count": len(courses),
    }


def build_student_portal_context(student):
    """Contexto ampliado para notes.views.dashboard."""
    pending_inst = _pending_activity_count(student)
    perf_bars = build_performance_bars(student)
    return {
        "enrollment_cards": build_enrollment_cards(student),
        "dashboard_activities": build_dashboard_activities(student),
        "institutional_pending_count": Submission.objects.filter(
            student=student,
            is_draft=False,
            status__in=[Submission.Status.SUBMITTED, Submission.Status.LATE],
            grade__isnull=True,
        ).count(),
        "pending_activity_count": pending_inst,
        "performance_bars": perf_bars,
        "show_performance_chart": len(perf_bars) > 0,
        "upcoming_evaluations": build_upcoming_evaluations(student),
        "next_class_hint": build_next_class_hint(student),
        "academic_calendar_events": (
            academic_calendar_events := build_academic_calendar_events(student)
        ),
        "academic_calendar_events_payload": build_academic_calendar_events_payload(
            academic_calendar_events
        ),
        **build_mini_calendar(student),
        **build_repaso_materials(student),
    }
