from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from academia.models import Offering
from accounts.decorators import role_required
from accounts.models import Student
from classroom.access import get_offering_for_teacher, teacher_owns_offering
from classroom.forms import AnnouncementForm, GradeSubmissionForm
from classroom.models import (
    AcademicWeek,
    Announcement,
    Forum,
    Grade,
    Submission,
)


def _teacher_offering_or_404(teacher, offering_id):
    return get_offering_for_teacher(teacher, offering_id)


@login_required
@role_required(Student.Role.TEACHER)
def manage_course(request, offering_id):
    teacher = request.user
    offering = _teacher_offering_or_404(teacher, offering_id)
    if not offering:
        messages.error(request, "No tiene asignado ese curso.")
        return redirect("dashboard_teacher")

    weeks = list(
        AcademicWeek.objects.filter(offering=offering)
        .annotate(
            material_count=Count("materials"),
            activity_count=Count("activities"),
        )
        .order_by("week_number")
    )
    announcements = Announcement.objects.filter(offering=offering).order_by(
        "-published_at"
    )[:20]
    forums = Forum.objects.filter(week__offering=offering).select_related(
        "week"
    ).order_by("-published_at")

    week_qs = AcademicWeek.objects.filter(offering=offering)
    offering_qs = Offering.objects.filter(pk=offering.id, teacher=teacher)

    if request.method == "POST" and request.POST.get("form_type") == "announcement":
        form = AnnouncementForm(request.POST)
        form.fields["offering"].queryset = offering_qs
        form.fields["week"].queryset = week_qs
        if form.is_valid():
            ann = form.save(commit=False)
            ann.author = teacher
            ann.save()
            messages.success(request, "Aviso publicado correctamente.")
            return redirect("classroom:teacher_manage_course", offering_id=offering.id)
        messages.error(request, "Revise los datos del aviso.")
    else:
        form = AnnouncementForm(initial={"offering": offering})
        form.fields["offering"].queryset = offering_qs
        form.fields["week"].queryset = week_qs

    return render(
        request,
        "classroom/teacher_manage_course.html",
        {
            "student": teacher,
            "portal_nav": "cursos",
            "offering": offering,
            "weeks": weeks,
            "announcements": announcements,
            "forums": forums,
            "announcement_form": form,
            "breadcrumbs": [
                {"label": "Inicio", "url": reverse("dashboard_teacher")},
                {
                    "label": "Mis cursos",
                    "url": reverse("dashboard_teacher") + "#cursos",
                },
                {"label": offering.name, "url": None},
            ],
        },
    )


@login_required
@role_required(Student.Role.TEACHER)
@require_http_methods(["POST"])
def toggle_forum_status(request, forum_id):
    teacher = request.user
    forum = get_object_or_404(
        Forum.objects.select_related("week__offering"),
        pk=forum_id,
    )
    if not teacher_owns_offering(teacher, forum.week.offering):
        messages.error(request, "No puede modificar este foro.")
        return redirect("dashboard_teacher")
    forum.status = (
        Forum.Status.CLOSED
        if forum.status == Forum.Status.OPEN
        else Forum.Status.OPEN
    )
    forum.save(update_fields=["status"])
    messages.success(
        request, f"Foro marcado como {forum.get_status_display().lower()}."
    )
    return redirect(reverse("dashboard_teacher") + "#foros")


@login_required
@role_required(Student.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def grade_submission(request, submission_id):
    teacher = request.user
    submission = get_object_or_404(
        Submission.objects.select_related(
            "student",
            "activity",
            "activity__week",
            "activity__week__offering",
        ),
        pk=submission_id,
        is_draft=False,
    )
    offering = submission.activity.week.offering
    if not teacher_owns_offering(teacher, offering):
        messages.error(request, "No puede calificar esta entrega.")
        return redirect("dashboard_teacher")

    grade = Grade.objects.filter(submission=submission).first()
    if request.method == "POST":
        form = GradeSubmissionForm(request.POST, instance=grade)
        if form.is_valid():
            g = form.save(commit=False)
            g.submission = submission
            g.graded_by = teacher
            g.save()
            submission.status = Submission.Status.GRADED
            submission.save(update_fields=["status"])
            messages.success(request, "Calificación guardada.")
            return redirect(reverse("dashboard_teacher") + "#entregas")
        messages.error(request, "Revise la nota ingresada.")
    else:
        form = GradeSubmissionForm(instance=grade)

    return render(
        request,
        "classroom/teacher_grade_submission.html",
        {
            "student": teacher,
            "submission": submission,
            "form": form,
            "offering": offering,
        },
    )
