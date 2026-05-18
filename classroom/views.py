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
    build_activity_page_context,
    build_course_page_context,
    build_enrollment_list_context,
    build_week_page_context,
)
from classroom.models import Submission
from classroom.submission_validation import validate_submission_file


def _render_classroom(request, template, context):
    base = {"portal_nav": "cursos"}
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

    if request.method == "POST":
        submission, _ = Submission.objects.get_or_create(
            activity=activity,
            student=student,
            defaults={"is_draft": True, "status": Submission.Status.DRAFT},
        )
        is_draft = request.POST.get("save_draft") == "1"
        comment = (request.POST.get("comment") or "").strip()
        uploaded = request.FILES.get("file")
        if uploaded:
            try:
                validate_submission_file(uploaded)
            except ValidationError as exc:
                messages.error(request, str(exc))
                return redirect("classroom:activity_submit", activity_id=activity_id)
            submission.file = uploaded
        submission.comment = comment

        if not is_draft:
            if request.POST.get("confirm_ready") != "1":
                messages.error(
                    request,
                    "Marque el checklist de verificación antes de entregar.",
                )
                return redirect("classroom:activity_submit", activity_id=activity_id)
            if not submission.file and not uploaded:
                messages.error(request, "Adjunte un archivo para entregar la actividad.")
                return redirect("classroom:activity_submit", activity_id=activity_id)

        if is_draft and activity.allows_draft:
            submission.is_draft = True
            submission.status = Submission.Status.DRAFT
            submission.submitted_at = None
            submission.save()
            messages.success(request, "Borrador guardado correctamente.")
        else:
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
            messages.success(request, "Actividad entregada correctamente.")
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
