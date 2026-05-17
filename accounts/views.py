import os
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login as login_student
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.models import *
from notes.models import Course
from accounts.forms import *
from accounts.decorators import role_required
from academia.models import AcademicPeriod, Enrollment, Offering, Program


@ensure_csrf_cookie
def login(request):
    if request.user.is_authenticated:
        messages.info(request, "Ya has iniciado sesión.")
        return redirect(request.user.get_dashboard_url_name())

    if request.method != "POST":
        form = EasyLearnAuthenticationForm()
    else:
        form = EasyLearnAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            student = authenticate(
                request,
                username=username,
                password=password,
            )

            if student is not None:
                login_student(request, student)
                if request.POST.get("remember_me"):
                    request.session.set_expiry(60 * 60 * 24 * 14)
                else:
                    request.session.set_expiry(0)
                return redirect(student.get_dashboard_url_name())
            messages.error(request, "Usuario o contraseña no válidos.")

    template_path = "registration/login.html"
    context = {"form": form}
    return render(request, template_path, context)


@login_required
@role_required(Student.Role.TEACHER)
def dashboard_teacher(request):
    """Panel docente — cursos ofertados asignados, matrículas e inscripciones reales."""
    Profile.objects.get_or_create(student=request.user)
    courses_qs = Course.objects.all().order_by("-updated")[:20]
    current_period = AcademicPeriod.objects.filter(is_current=True).first()
    period_label = current_period.name if current_period else "Sin período actual marcado"

    teaching_offerings_qs = (
        Offering.objects.filter(teacher=request.user)
        .select_related("program", "period")
        .annotate(
            active_student_count=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
            ),
        )
        .order_by("-period__name", "program__name", "code")
    )
    assigned_offering_count = teaching_offerings_qs.count()
    teaching_offerings = list(teaching_offerings_qs[:40])
    max_bar_students = (
        max((o.active_student_count for o in teaching_offerings), default=0) or 1
    )

    teacher_enrollments_active = Enrollment.objects.filter(
        offering__teacher=request.user,
        status=Enrollment.Status.ACTIVE,
    )
    teacher_active_matricula_count = teacher_enrollments_active.count()
    distinct_student_count = (
        teacher_enrollments_active.values("student_id").distinct().count()
    )
    thirty_days_ago = timezone.now() - timedelta(days=30)
    teacher_recent_enrollment_30d = teacher_enrollments_active.filter(
        enrolled_at__gte=thirty_days_ago
    ).count()

    recent_teaching_enrollments = list(
        teacher_enrollments_active.select_related(
            "student",
            "offering",
            "offering__program",
            "offering__period",
        ).order_by("-enrolled_at")[:35]
    )

    # Cuando exista modelo de entregas vinculado a actividades, sustituir por conteo real.
    pending_delivery_count = 0

    return render(
        request,
        "easylearn/teacher_portal.html",
        {
            "student": request.user,
            "portal_role_label": "Docente",
            "courses": courses_qs,
            "assigned_course_count": Course.objects.count(),
            "teaching_offerings": teaching_offerings,
            "assigned_offering_count": assigned_offering_count,
            "distinct_student_count": distinct_student_count,
            "pending_delivery_count": pending_delivery_count,
            "teacher_active_matricula_count": teacher_active_matricula_count,
            "teacher_recent_enrollment_30d": teacher_recent_enrollment_30d,
            "recent_teaching_enrollments": recent_teaching_enrollments,
            "max_bar_students": max_bar_students,
            "period_label": period_label,
            "current_period": current_period,
            "header_search_action": reverse("dashboard_teacher"),
            "header_search_placeholder": "Buscar en tablero: cursos, actividades, entregas…",
            "header_search_label": "Filtrar contenido del tablero docente",
        },
    )


@login_required
@role_required(Student.Role.ADMIN)
def dashboard_admin(request):
    """Panel administrador — usuarios, cursos y alertas institucionales (MER)."""
    Profile.objects.get_or_create(student=request.user)
    User = get_user_model()
    courses_qs = Course.objects.all().order_by("-updated")[:12]
    recent_users = (
        User.objects.select_related("academic_program")
        .all()
        .order_by("-date_joined")[:10]
    )
    teacher_count = User.objects.filter(role=Student.Role.TEACHER).count()
    student_role_count = User.objects.filter(role=Student.Role.STUDENT).count()

    current_period = AcademicPeriod.objects.filter(is_current=True).first()
    period_label = current_period.name if current_period else "Sin período actual marcado"
    program_count = Program.objects.count()
    period_count = AcademicPeriod.objects.count()
    offering_count = Offering.objects.count()
    active_enrollment_count = Enrollment.objects.filter(
        status=Enrollment.Status.ACTIVE
    ).count()
    offerings_without_teacher = Offering.objects.filter(teacher__isnull=True).count()

    recent_offerings = (
        Offering.objects.select_related("program", "period", "teacher")
        .annotate(
            active_student_count=Count(
                "enrollments",
                filter=Q(enrollments__status=Enrollment.Status.ACTIVE),
            ),
        )
        .order_by("-period__name", "program__name", "code")[:15]
    )
    recent_enrollments = (
        Enrollment.objects.filter(status=Enrollment.Status.ACTIVE)
        .select_related("student", "offering", "offering__program", "offering__period")
        .order_by("-enrolled_at")[:12]
    )
    recent_periods = AcademicPeriod.objects.order_by("-name")[:12]
    withdrawn_enrollment_count = Enrollment.objects.filter(
        status=Enrollment.Status.WITHDRAWN
    ).count()
    students_missing_program_count = User.objects.filter(
        role=Student.Role.STUDENT,
        academic_program__isnull=True,
    ).count()
    active_user_count = User.objects.filter(is_active=True).count()

    return render(
        request,
        "easylearn/admin_portal.html",
        {
            "student": request.user,
            "portal_role_label": "Administrador",
            "user": request.user,
            "user_count": User.objects.count(),
            "active_user_count": active_user_count,
            "course_count": Course.objects.count(),
            "teacher_count": teacher_count,
            "student_role_count": student_role_count,
            "recent_users": recent_users,
            "recent_courses": courses_qs,
            "recent_offerings": recent_offerings,
            "recent_enrollments": recent_enrollments,
            "recent_periods": recent_periods,
            "period_count": period_count,
            "program_count": program_count,
            "offering_count": offering_count,
            "active_enrollment_count": active_enrollment_count,
            "withdrawn_enrollment_count": withdrawn_enrollment_count,
            "students_missing_program_count": students_missing_program_count,
            "offerings_without_teacher": offerings_without_teacher,
            "current_period": current_period,
            "period_label": period_label,
            "header_search_action": reverse("dashboard_admin"),
            "header_search_placeholder": "Buscar usuarios, cursos, roles…",
            "header_search_label": "Filtrar tablero administrador",
        },
    )


@login_required
def profile(request, user_id=None, username=None):
    student = request.user

    Profile.objects.get_or_create(student=student)

    profile = student.profile
    courses = Course.objects.filter(student_id=student.id)

    template_path = "accounts/profile.html"
    context = {
        "student": student,
        "profile": profile,
        "section": "profile",
        "courses": courses,
    }
    return render(request, template_path, context)


@login_required
def edit_profile(request):
    student = request.user
    profile = student.profile
    if request.method != "POST":
        student_update_form = StudentUpdateForm(instance=student)
        profile_edit_form = ProfileEditForm(instance=profile)
    else:
        student_update_form = StudentUpdateForm(
            instance=student,
            data=request.POST,
        )
        profile_edit_form = ProfileEditForm(
            instance=profile,
            data=request.POST,
            files=request.FILES,
        )
        if student_update_form.is_valid() and profile_edit_form.is_valid():
            student_update_form.save()
            profile_edit_form.save()
            messages.success(request, "Profile Updated successfully")
            return redirect(student.profile)
        else:
            messages.error(request, "Error Updating Your Profile")

    template_path = "accounts/edit_profile.html"
    context = {
        "student_update_form": student_update_form,
        "profile_edit_form": profile_edit_form,
        "section": "profile",
    }
    return render(request, template_path, context)


@login_required
def delete_account(request):
    student = request.user
    student.delete()
    request.session.flush()
    messages.success(request, "You have deleted your account successfully")
    return redirect("login")
