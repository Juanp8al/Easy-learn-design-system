"""Control de acceso al aula por rol."""

from django.shortcuts import get_object_or_404

from academia.models import Enrollment, Offering
from accounts.models import Student

from .models import AcademicWeek, Activity


def get_student_enrollment(student, offering_id):
    return (
        Enrollment.objects.filter(
            student=student,
            offering_id=offering_id,
            status=Enrollment.Status.ACTIVE,
        )
        .select_related("offering", "offering__teacher", "offering__program", "offering__period")
        .first()
    )


def get_offering_for_student(student, offering_id):
    enrollment = get_student_enrollment(student, offering_id)
    return enrollment.offering if enrollment else None


def get_week_for_student(student, week_id):
    week = get_object_or_404(
        AcademicWeek.objects.select_related(
            "offering",
            "offering__teacher",
            "offering__program",
            "offering__period",
        ),
        pk=week_id,
    )
    if not get_student_enrollment(student, week.offering_id):
        return None
    return week


def get_week_for_student_by_number(student, offering_id, week_number):
    if not get_student_enrollment(student, offering_id):
        return None
    return (
        AcademicWeek.objects.filter(
            offering_id=offering_id,
            week_number=week_number,
        )
        .select_related(
            "offering",
            "offering__teacher",
            "offering__program",
            "offering__period",
        )
        .first()
    )


def get_activity_for_student(student, activity_id):
    activity = get_object_or_404(
        Activity.objects.select_related(
            "week",
            "week__offering",
            "week__offering__teacher",
        ),
        pk=activity_id,
        status=Activity.Status.PUBLISHED,
    )
    if not get_student_enrollment(student, activity.week.offering_id):
        return None
    return activity


def teacher_owns_offering(teacher, offering):
    return offering.teacher_id == teacher.pk


def get_offering_for_teacher(teacher, offering_id):
    return (
        Offering.objects.filter(pk=offering_id, teacher=teacher)
        .select_related("program", "period")
        .first()
    )
