"""Contexto del aula para plantillas del portal estudiante."""

from django.db.models import Avg, Prefetch

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
    from classroom.portal import build_week_navigation, describe_activity_status

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
    prev_n, next_n = build_week_navigation(week.offering, week.week_number)
    return {
        "current_offering": week.offering,
        "current_week": week,
        "week_materials": week_materials,
        "week_activities": week_activities,
        "week_prev_number": prev_n,
        "week_next_number": next_n,
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
    }


def build_enrollment_list_context(student):
    enrollments = (
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE)
        .select_related(
            "offering",
            "offering__program",
            "offering__period",
            "offering__teacher",
        )
        .order_by("-offering__period__name", "offering__program__name", "offering__code")
    )
    return {"academic_enrollments": enrollments}


def build_grades_context(student):
    """Calificaciones institucionales desde entregas calificadas."""
    grades = (
        Grade.objects.filter(submission__student=student)
        .select_related(
            "submission",
            "submission__activity",
            "submission__activity__week",
            "submission__activity__week__offering",
            "submission__activity__week__offering__teacher",
            "graded_by",
        )
        .order_by("-graded_at")
    )

    grade_rows = []
    for g in grades:
        act = g.submission.activity
        grade_rows.append(
            {
                "grade": g,
                "activity": act,
                "offering": act.week.offering,
                "submitted_at": g.submission.submitted_at,
            }
        )

    offering_averages = {}
    for row in grade_rows:
        off = row["offering"]
        if off.id not in offering_averages:
            offering_averages[off.id] = {"offering": off, "scores": []}
        offering_averages[off.id]["scores"].append(row["grade"].score)

    offering_grade_summary = []
    for item in offering_averages.values():
        scores = item["scores"]
        avg = sum(scores) / len(scores) if scores else None
        offering_grade_summary.append(
            {
                "offering": item["offering"],
                "average": round(avg, 2) if avg is not None else None,
            }
        )

    pending_grade_count = (
        Submission.objects.filter(
            student=student,
            is_draft=False,
            status__in=[Submission.Status.SUBMITTED, Submission.Status.LATE],
        )
        .filter(grade__isnull=True)
        .count()
    )

    all_graded = Grade.objects.filter(submission__student=student)
    overall_avg = all_graded.aggregate(avg=Avg("score"))["avg"]
    overall_avg_display = round(float(overall_avg), 2) if overall_avg is not None else None

    avg_by_offering = {item["offering"].id: item["average"] for item in offering_grade_summary}
    enrollment_grade_rows = []
    enrollments = (
        Enrollment.objects.filter(
            student=student,
            status=Enrollment.Status.ACTIVE,
        )
        .select_related("offering", "offering__teacher")
        .order_by("-offering__period__name", "offering__code")
    )
    for enr in enrollments:
        enrollment_grade_rows.append(
            {
                "offering": enr.offering,
                "average": avg_by_offering.get(enr.offering_id),
            }
        )

    return {
        "grade_rows": grade_rows,
        "offering_grade_summary": offering_grade_summary,
        "enrollment_grade_rows": enrollment_grade_rows,
        "pending_grade_count": pending_grade_count,
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


