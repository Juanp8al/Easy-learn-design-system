"""Contexto del portal estudiante (Inicio, Mis cursos, Calendario, Mensajes)."""

import json
from calendar import monthrange
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from academia.models import Enrollment
from classroom.context import _submission_stats_for_offering
from classroom.models import AcademicWeek, Activity, Announcement, Grade, Submission


def describe_activity_status(activity, submission=None):
    """Estado visual de una actividad para el estudiante."""
    now = timezone.now()
    if submission and submission.grade_id:
        return {
            "status_label": "Calificada",
            "badge": "ok",
            "state": "graded",
            "is_overdue": False,
        }
    if submission and not submission.is_draft:
        return {
            "status_label": "Entregada",
            "badge": "draft",
            "state": "submitted",
            "is_overdue": False,
        }
    overdue = bool(activity.due_at and activity.due_at < now)
    if overdue:
        return {
            "status_label": "Vencida",
            "badge": "warn",
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


def build_enrollment_cards(student):
    """Tarjetas de curso institucional con avance y semana actual."""
    enrollments = (
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
        .select_related("offering", "offering__teacher", "offering__period")
        .order_by("-offering__period__name", "offering__code")
    )
    cards = []
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
        stats = _submission_stats_for_offering(student, off)
        cards.append(
            {
                "enrollment": enr,
                "offering": off,
                "current_week": current_week,
                "progress_pct": progress_pct,
                "stats": stats,
            }
        )
    return cards


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
        if sub and sub.grade_id:
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
    """Eventos para la vista Calendario (entregas)."""
    now = timezone.now()
    offering_ids = list(_active_offering_ids(student))
    events = []
    for act in (
        Activity.objects.filter(
            week__offering_id__in=offering_ids,
            status=Activity.Status.PUBLISHED,
        )
        .exclude(due_at__isnull=True)
        .select_related("week", "week__offering")
        .order_by("due_at")[:60]
    ):
        meta = describe_activity_status(
            act, Submission.objects.filter(activity=act, student=student).first()
        )
        events.append(
            {
                "date": timezone.localtime(act.due_at).date(),
                "time_label": timezone.localtime(act.due_at).strftime("%H:%M"),
                "title": act.title,
                "offering_code": act.week.offering.code,
                "type": "entrega",
                "status_label": meta["status_label"],
                "url": reverse("classroom:activity_submit", args=[act.id]),
            }
        )
    return events


def build_portal_messages(student):
    """Avisos de docentes y mensajes del sistema."""
    offering_ids = list(_active_offering_ids(student))
    msgs = []
    for ann in (
        Announcement.objects.filter(offering_id__in=offering_ids)
        .select_related("offering", "author", "week")
        .order_by("-published_at")[:40]
    ):
        msgs.append(
            {
                "title": ann.title,
                "preview": (ann.content or "")[:160],
                "when": ann.published_at,
                "source": "docente",
                "author": ann.author.get_full_name() if ann.author else ann.offering.teacher,
                "offering_code": ann.offering.code,
                "priority": ann.priority,
            }
        )
    if not msgs:
        msgs.append(
            {
                "title": "Bienvenido a EasyLearn",
                "preview": "Consulte el aula virtual, entregas y calificaciones desde el menú lateral.",
                "when": timezone.now(),
                "source": "sistema",
                "author": "Sistema",
                "offering_code": "",
                "priority": "normal",
            }
        )
    msgs.sort(key=lambda m: m["when"], reverse=True)
    return msgs[:30]


def build_course_extras(student, offering):
    """Recordatorios en panorama del curso."""
    today = timezone.localdate()
    now = timezone.now()
    due_today = []
    for act in Activity.objects.filter(
        week__offering=offering,
        status=Activity.Status.PUBLISHED,
        due_at__date=today,
    ).order_by("due_at"):
        sub = Submission.objects.filter(activity=act, student=student).first()
        meta = describe_activity_status(act, sub)
        if meta["state"] in ("pending", "overdue"):
            due_today.append({"activity": act, **meta})

    current_week = (
        AcademicWeek.objects.filter(offering=offering)
        .filter(status=AcademicWeek.Status.IN_PROGRESS)
        .order_by("week_number")
        .first()
    )
    schedule_hint = None
    if current_week and current_week.starts_on and current_week.ends_on:
        schedule_hint = (
            f"Semana {current_week.week_number}: "
            f"{current_week.starts_on.strftime('%d %b')} – {current_week.ends_on.strftime('%d %b')}"
        )

    return {
        "current_week_highlight": current_week,
        "course_due_today": due_today,
        "course_schedule_hint": schedule_hint,
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
        "academic_calendar_events": build_academic_calendar_events(student),
        "portal_messages": build_portal_messages(student),
        **build_mini_calendar(student),
    }
