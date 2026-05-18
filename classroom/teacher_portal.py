"""Contexto del portal docente (hash UI + datos reales)."""

from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.urls import reverse
from django.utils import timezone

from academia.models import Enrollment, Offering
from classroom.models import (
    AcademicWeek,
    Activity,
    Announcement,
    Forum,
    Grade,
    Submission,
)


def _teacher_offerings(teacher):
    return (
        Offering.objects.filter(teacher=teacher)
        .select_related("program", "period")
        .annotate(
            active_student_count=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
            ),
        )
        .order_by("-period__name", "program__name", "code")
    )


def build_teacher_next_class_hint(teacher):
    now = timezone.now()
    act = (
        Activity.objects.filter(
            week__offering__teacher=teacher,
            status=Activity.Status.PUBLISHED,
            due_at__gte=now,
        )
        .select_related("week", "week__offering")
        .order_by("due_at")
        .first()
    )
    if act:
        return {
            "label": act.title[:48],
            "sub": f"{act.week.offering.code} · límite {timezone.localtime(act.due_at).strftime('%d %b, %H:%M')}",
        }
    week = (
        AcademicWeek.objects.filter(
            offering__teacher=teacher,
            starts_on__gte=now.date(),
        )
        .select_related("offering")
        .order_by("starts_on")
        .first()
    )
    if week:
        return {
            "label": f"Semana {week.week_number}",
            "sub": f"{week.offering.code} · inicia {week.starts_on.strftime('%d %b')}",
        }
    return None


def build_teacher_delivery_activity_rows(teacher):
    """Filas por actividad: entregas, límite, estado."""
    now = timezone.now()
    today = timezone.localdate()
    activities = (
        Activity.objects.filter(week__offering__teacher=teacher)
        .select_related("week", "week__offering")
        .order_by("week__offering__code", "week__week_number", "due_at", "title")
    )
    rows = []
    for act in activities:
        base = Submission.objects.filter(
            activity=act,
            is_draft=False,
        ).exclude(status=Submission.Status.DRAFT)
        pending = base.filter(grade__isnull=True).count()
        graded = base.filter(grade__isnull=False).count()
        total = base.count()
        due_today = bool(act.due_at and timezone.localtime(act.due_at).date() == today)
        overdue = bool(act.due_at and act.due_at < now)
        if pending > 0:
            status_label = "Pendiente de nota"
            badge = "warn"
        elif graded > 0 and pending == 0:
            status_label = "Calificada"
            badge = "ok"
        else:
            status_label = act.get_status_display()
            badge = "draft"
        rows.append(
            {
                "activity": act,
                "offering": act.week.offering,
                "week": act.week,
                "pending_count": pending,
                "graded_count": graded,
                "submission_count": total,
                "due_today": due_today,
                "overdue": overdue,
                "status_label": status_label,
                "badge": badge,
                "offering_id": act.week.offering_id,
                "week_number": act.week.week_number,
            }
        )
    return rows


def build_teacher_forums_list(teacher):
    return list(
        Forum.objects.filter(week__offering__teacher=teacher)
        .select_related("week", "week__offering")
        .order_by("-published_at")[:50]
    )


def build_teacher_announcements_list(teacher):
    return list(
        Announcement.objects.filter(offering__teacher=teacher)
        .select_related("offering", "week")
        .order_by("-published_at")[:50]
    )


def build_teacher_grade_summary(teacher):
    """Promedio por asignatura cuando hay Grade."""
    offerings = list(_teacher_offerings(teacher))
    summaries = []
    has_any_grade = False
    for off in offerings:
        avg = Grade.objects.filter(
            submission__activity__week__offering=off,
        ).aggregate(a=Avg("score"))["a"]
        graded_count = Grade.objects.filter(
            submission__activity__week__offering=off,
        ).count()
        if graded_count:
            has_any_grade = True
        summaries.append(
            {
                "offering": off,
                "average": round(float(avg), 2) if avg is not None else None,
                "graded_count": graded_count,
            }
        )
    return summaries, has_any_grade


def build_teacher_upcoming_dates(teacher, limit=5):
    now = timezone.now()
    acts = (
        Activity.objects.filter(
            week__offering__teacher=teacher,
            status=Activity.Status.PUBLISHED,
            due_at__gte=now,
        )
        .select_related("week__offering")
        .order_by("due_at")[:limit]
    )
    return [
        {
            "title": a.title,
            "code": a.week.offering.code,
            "due_at": a.due_at,
        }
        for a in acts
    ]


def build_teacher_portal_context(teacher):
    from classroom.context import build_teacher_submissions_context

    offerings = list(_teacher_offerings(teacher)[:40])
    sub_ctx = build_teacher_submissions_context(teacher)
    grade_summaries, has_grade_data = build_teacher_grade_summary(teacher)
    delivery_rows = build_teacher_delivery_activity_rows(teacher)

    teacher_enrollments_active = Enrollment.objects.filter(
        offering__teacher=teacher,
        status=Enrollment.Status.ACTIVE,
    )
    distinct_student_count = (
        teacher_enrollments_active.values("student_id").distinct().count()
    )

    offering_filter_choices = [
        {"id": o.id, "code": o.code, "name": o.name} for o in offerings
    ]

    return {
        "teaching_offerings": offerings,
        "assigned_offering_count": len(offerings),
        "distinct_student_count": distinct_student_count,
        "teacher_next_class_hint": build_teacher_next_class_hint(teacher),
        "teacher_upcoming_dates": build_teacher_upcoming_dates(teacher),
        "teacher_delivery_rows": delivery_rows,
        "teacher_forums": build_teacher_forums_list(teacher),
        "teacher_announcements": build_teacher_announcements_list(teacher),
        "teacher_grade_summaries": grade_summaries,
        "teacher_has_grade_data": has_grade_data,
        "teacher_offering_filter_choices": offering_filter_choices,
        **sub_ctx,
    }
