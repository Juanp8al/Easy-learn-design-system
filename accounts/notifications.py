"""Notificaciones del portal (campana)."""

from django.urls import reverse
from django.utils import timezone

from accounts.models import UserNotification


def push_notification(user, *, kind, title, message="", link=""):
    if user is None:
        return None
    user_id = user if isinstance(user, int) else getattr(user, "pk", None)
    if not user_id:
        return None
    return UserNotification.objects.create(
        user_id=user_id,
        kind=kind,
        title=title,
        message=message,
        link=link or "",
    )


def get_portal_notifications(user, limit=20):
    if not user.is_authenticated:
        return [], 0
    qs = UserNotification.objects.filter(user=user).order_by("-created_at")[:limit]
    items = list(qs)
    unread = UserNotification.objects.filter(user=user, read_at__isnull=True).count()
    return items, unread


def mark_notifications_read(user, notification_id=None):
    qs = UserNotification.objects.filter(user=user, read_at__isnull=True)
    if notification_id:
        qs = qs.filter(pk=notification_id)
    return qs.update(read_at=timezone.now())


def notify_grade_published(grade):
    submission = grade.submission
    activity = submission.activity
    offering = activity.offering
    link = reverse("classroom:activity_submit", args=[activity.pk])
    push_notification(
        submission.student,
        kind=UserNotification.Kind.GRADE,
        title=f"Nueva calificación · {activity.title}",
        message=f"{offering.code}: nota {grade.score}.",
        link=link,
    )


def notify_due_date_changed(activity, previous_due):
    if previous_due is None or not activity.due_at or previous_due == activity.due_at:
        return
    from academia.models import Enrollment

    students = Enrollment.objects.filter(
        offering=activity.offering,
        status=Enrollment.Status.ACTIVE,
    ).values_list("student_id", flat=True)
    when = activity.due_at.strftime("%d/%m/%Y %H:%M")
    link = reverse(
        "classroom:week_detail",
        args=[activity.offering_id, activity.week.week_number],
    )
    for student_id in students:
        push_notification(
            student_id,
            kind=UserNotification.Kind.DUE_DATE,
            title=f"Fecha actualizada · {activity.title}",
            message=f"Nueva fecha límite: {when}.",
            link=link,
        )


def notify_announcement(announcement):
    from academia.models import Enrollment

    students = Enrollment.objects.filter(
        offering=announcement.offering,
        status=Enrollment.Status.ACTIVE,
    ).values_list("student_id", flat=True)
    link = reverse("classroom:course_detail", args=[announcement.offering_id])
    preview = (announcement.content or "")[:120]
    for student_id in students:
        push_notification(
            student_id,
            kind=UserNotification.Kind.ANNOUNCEMENT,
            title=announcement.title,
            message=preview,
            link=link,
        )
