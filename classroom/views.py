from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.decorators import role_required
from accounts.models import Student
from classroom.access import (
    get_activity_for_student,
    get_offering_for_student,
    get_week_for_student,
    get_week_for_student_by_number,
)
from classroom.breadcrumbs import (
    activity_crumbs,
    course_crumbs,
    student_home_crumbs,
    week_crumbs,
)
from classroom.context import (
    build_activity_labels,
    build_activity_page_context,
    build_course_page_context,
    build_enrollment_list_context,
    build_week_page_context,
)
from classroom.models import Grade, Submission
from classroom.portal import describe_activity_status
from classroom.submission_validation import validate_submission_file


def _render_classroom(request, template, context):
    from django.urls import reverse

    base = {
        "portal_nav": "cursos",
        "header_search_action": reverse("notes:dashboard"),
        "header_search_placeholder": "Buscar cursos, actividades, recursos…",
        "header_search_label": "Buscar cursos, actividades o recursos",
    }
    base.update(context)
    return render(request, template, base)


@login_required
@role_required(Student.Role.STUDENT)
def course_list(request):
    student = request.user
    crumbs = student_home_crumbs()
    crumbs[-1] = {"label": "Mis cursos", "url": None}
    ctx = build_enrollment_list_context(student)
    return _render_classroom(
        request,
        "classroom/course_list.html",
        {"student": student, "breadcrumbs": crumbs, **ctx},
    )


@login_required
@role_required(Student.Role.STUDENT)
def course_detail(request, offering_id):
    student = request.user
    offering = get_offering_for_student(student, offering_id)
    if not offering:
        messages.error(request, "No tienes matrícula activa en ese curso.")
        return redirect("classroom:course_list")
    ctx = build_course_page_context(student, offering)
    return _render_classroom(
        request,
        "classroom/course.html",
        {
            "student": student,
            "breadcrumbs": course_crumbs(offering),
            **ctx,
        },
    )


@login_required
@role_required(Student.Role.STUDENT)
def week_detail(request, offering_id, week_number):
    student = request.user
    week = get_week_for_student_by_number(student, offering_id, week_number)
    if not week:
        messages.error(request, "No puedes acceder a esa semana.")
        return redirect("classroom:course_detail", offering_id=offering_id)
    ctx = build_week_page_context(student, week)
    return _render_classroom(
        request,
        "classroom/week.html",
        {
            "student": student,
            "breadcrumbs": week_crumbs(week.offering, week),
            **ctx,
        },
    )


@login_required
@role_required(Student.Role.STUDENT)
@require_http_methods(["GET", "POST"])
def activity_submit(request, activity_id):
    student = request.user
    activity = get_activity_for_student(student, activity_id)
    if not activity:
        messages.error(request, "No puedes acceder a esa actividad.")
        return redirect("classroom:course_list")

    offering = activity.week.offering
    week = activity.week

    submission = Submission.objects.filter(activity=activity, student=student).first()
    status_meta = describe_activity_status(activity, submission)
    if status_meta["state"] == "overdue":
        messages.error(
            request,
            "La fecha límite de esta actividad ya venció. Ya no puede verla ni entregarla.",
        )
        return redirect(
            "classroom:week_detail",
            offering_id=offering.id,
            week_number=week.week_number,
        )

    if request.method == "POST":
        submission, _ = Submission.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={"is_draft": True, "status": Submission.Status.DRAFT},
        )
        labels = build_activity_labels(activity)
        is_graded = Grade.objects.filter(submission=submission).exists()

        comment = (request.POST.get("comment") or "").strip()
        uploaded = request.FILES.get("file")

        if request.POST.get("clear_file") == "1" and not uploaded and submission.file:
            submission.file.delete(save=False)
            submission.file = None

        if uploaded:
            try:
                validate_submission_file(uploaded)
            except ValidationError as exc:
                messages.error(request, str(exc))
                return redirect("classroom:activity_submit", activity_id=activity_id)
            if submission.file:
                submission.file.delete(save=False)
            submission.file = uploaded

        submission.comment = comment

        if is_graded:
            messages.error(request, "No puede modificar una entrega ya calificada.")
            return redirect("classroom:activity_submit", activity_id=activity_id)

        if request.POST.get("confirm_ready") != "1":
            messages.error(request, labels["submit_error_checklist"])
            return redirect("classroom:activity_submit", activity_id=activity_id)

        needs_file = labels["requires_file"]
        has_content = bool(uploaded or submission.file or comment)
        if needs_file and not submission.file and not uploaded:
            messages.error(request, labels["submit_error_empty"])
            return redirect("classroom:activity_submit", activity_id=activity_id)
        if not needs_file and not has_content:
            messages.error(request, labels["submit_error_empty"])
            return redirect("classroom:activity_submit", activity_id=activity_id)

        submission.is_draft = False
        submission.submitted_at = timezone.now()
        if (
            activity.due_at
            and submission.submitted_at > activity.due_at
            and not activity.allow_late
        ):
            messages.error(request, "La fecha límite de esta actividad ya venció.")
            return redirect("classroom:activity_submit", activity_id=activity_id)
        submission.status = (
            Submission.Status.LATE
            if activity.due_at and submission.submitted_at > activity.due_at
            else Submission.Status.SUBMITTED
        )
        submission.save()
        messages.success(request, labels["submit_success"])
        return redirect("classroom:activity_submit", activity_id=activity_id)

    ctx = build_activity_page_context(student, activity)
    return _render_classroom(
        request,
        "classroom/activity_submit.html",
        {
            "student": student,
            "breadcrumbs": activity_crumbs(offering, week, activity),
            **ctx,
        },
    )


# Compatibilidad con enlaces antiguos (redirigen a URL canónica)
@login_required
@role_required(Student.Role.STUDENT)
def enter_offering(request, offering_id):
    return redirect("classroom:course_detail", offering_id=offering_id)


@login_required
@role_required(Student.Role.STUDENT)
def enter_week(request, week_id):
    week = get_week_for_student(request.user, week_id)
    if not week:
        messages.error(request, "No puedes acceder a esa semana.")
        return redirect("classroom:course_list")
    return redirect(
        "classroom:week_detail",
        offering_id=week.offering_id,
        week_number=week.week_number,
    )


@login_required
@role_required(Student.Role.STUDENT)
def enter_activity(request, activity_id):
    return redirect("classroom:activity_submit", activity_id=activity_id)
