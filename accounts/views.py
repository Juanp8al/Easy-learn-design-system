import os
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as login_student,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.http import HttpResponseNotFound, JsonResponse
from django.conf import settings

from accounts.models import *
from notes.models import Course
from accounts.forms import *
from django.contrib.auth.views import PasswordChangeView
from accounts.decorators import role_required
from academia.admin_portal import build_admin_portal_context
from academia.models import AcademicPeriod, Enrollment, Offering, Program
from classroom.teacher_portal import build_teacher_portal_context
from accounts.notifications import mark_notifications_read

REMEMBER_ME_COOKIE = "el_remember_me"
REMEMBER_USERNAME_COOKIE = "el_remember_username"
REMEMBER_MAX_AGE = 60 * 60 * 24 * 14  # 14 días


def _remember_cookie_kwargs():
    return {"max_age": REMEMBER_MAX_AGE, "samesite": "Lax", "path": "/"}


def _apply_remember_cookies(response, username, remember):
    if remember:
        response.set_cookie(
            REMEMBER_USERNAME_COOKIE,
            username,
            **_remember_cookie_kwargs(),
        )
        response.set_cookie(REMEMBER_ME_COOKIE, "1", **_remember_cookie_kwargs())
    else:
        response.delete_cookie(REMEMBER_USERNAME_COOKIE, path="/")
        response.delete_cookie(REMEMBER_ME_COOKIE, path="/")
    return response


def _login_remember_context(request):
    remember = request.COOKIES.get(REMEMBER_ME_COOKIE) == "1"
    username = (request.COOKIES.get(REMEMBER_USERNAME_COOKIE) or "").strip()
    return {
        "remember_me_checked": remember,
        "remember_username": username,
    }


@ensure_csrf_cookie
def login(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url_name())

    remember_ctx = _login_remember_context(request)

    if request.method != "POST":
        initial = {}
        if remember_ctx["remember_username"]:
            initial["username"] = remember_ctx["remember_username"]
        form = EasyLearnAuthenticationForm(initial=initial)
    else:
        remember = bool(request.POST.get("remember_me"))
        remember_ctx["remember_me_checked"] = remember
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
                if remember:
                    request.session.set_expiry(REMEMBER_MAX_AGE)
                else:
                    request.session.set_expiry(0)
                response = redirect(student.get_dashboard_url_name())
                _apply_remember_cookies(response, username, remember)
                return response
            messages.error(request, "Usuario o contraseña no válidos.")

    template_path = "registration/login.html"
    context = {"form": form, **remember_ctx}
    response = render(request, template_path, context)
    if request.method == "POST" and not request.POST.get("remember_me"):
        _apply_remember_cookies(response, "", False)
    return response


@login_required
@role_required(Student.Role.TEACHER)
def dashboard_teacher(request):
    """Panel docente — cursos ofertados asignados, matrículas e inscripciones reales."""
    Profile.objects.get_or_create(student=request.user)
    current_period = AcademicPeriod.objects.filter(is_current=True).first()
    period_label = current_period.name if current_period else "Sin período actual marcado"

    teacher_enrollments_active = Enrollment.objects.filter(
        offering__teacher=request.user,
        status=Enrollment.Status.ACTIVE,
    )
    teacher_active_matricula_count = teacher_enrollments_active.count()
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
    teaching_offerings = []
    max_bar_students = 1
    portal_ctx = build_teacher_portal_context(request.user)
    teaching_offerings = portal_ctx.get("teaching_offerings", [])
    max_bar_students = (
        max((o.active_student_count for o in teaching_offerings), default=0) or 1
    )

    return render(
        request,
        "easylearn/teacher_portal.html",
        {
            "student": request.user,
            "portal_role_label": "Docente",
            "teacher_active_matricula_count": teacher_active_matricula_count,
            "teacher_recent_enrollment_30d": teacher_recent_enrollment_30d,
            "recent_teaching_enrollments": recent_teaching_enrollments,
            "max_bar_students": max_bar_students,
            "period_label": period_label,
            "current_period": current_period,
            "pending_delivery_count": portal_ctx.get(
                "teacher_pending_submission_count", 0
            ),
            "header_search_action": reverse("dashboard_teacher"),
            "header_search_placeholder": "Buscar en tablero: cursos, actividades, entregas…",
            "header_search_label": "Filtrar contenido del tablero docente",
            **portal_ctx,
        },
    )


@login_required
@role_required(Student.Role.ADMIN)
def dashboard_admin(request):
    """Panel administrador — usuarios, cursos y alertas institucionales."""
    Profile.objects.get_or_create(student=request.user)
    return render(
        request,
        "easylearn/admin_portal.html",
        {
            "student": request.user,
            "portal_role_label": "Administrador",
            "user": request.user,
            "header_search_action": reverse("dashboard_admin"),
            "header_search_placeholder": "Buscar usuarios, cursos, roles…",
            "header_search_label": "Filtrar tablero administrador",
            **build_admin_portal_context(),
        },
    )


def _portal_profile_context(student):
    Profile.objects.get_or_create(student=student)
    student = Student.objects.select_related("academic_program", "profile").get(
        pk=student.pk
    )
    role_labels = {
        Student.Role.STUDENT: "Estudiante",
        Student.Role.TEACHER: "Docente",
        Student.Role.ADMIN: "Administrador",
    }
    enrollments = []
    teaching_offerings = []
    if student.role == Student.Role.STUDENT:
        enrollments = list(
            Enrollment.objects.filter(
                student=student,
                status=Enrollment.Status.ACTIVE,
            )
            .select_related("offering", "offering__period")
            .order_by("-offering__period__name", "offering__code")[:24]
        )
    elif student.role == Student.Role.TEACHER:
        teaching_offerings = list(
            Offering.objects.filter(teacher=student)
            .select_related("period")
            .order_by("-period__name", "code")[:24]
        )

    dashboard_url_name = student.get_dashboard_url_name()
    return {
        "student": student,
        "profile": student.profile,
        "portal_role_label": role_labels.get(student.role, "Usuario"),
        "courses": Course.objects.filter(student_id=student.id).order_by("-updated")[:12],
        "enrollments": enrollments,
        "teaching_offerings": teaching_offerings,
        "portal_dashboard_url": reverse(dashboard_url_name),
        "timezone_label": settings.TIME_ZONE.replace("_", "/"),
        "last_login_display": student.last_login,
    }


@login_required
def profile(request, user_id=None, username=None):
    student = request.user
    if user_id is not None and user_id != student.id:
        return redirect("profile")

    password_form = PortalPasswordChangeForm(user=student)
    if request.method == "POST" and request.POST.get("form_type") == "password":
        password_form = PortalPasswordChangeForm(user=student, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Su contraseña se actualizó correctamente.")
            return redirect("profile")
        messages.error(
            request,
            "No se pudo cambiar la contraseña. Verifique la contraseña actual y que la nueva coincida.",
        )

    ctx = _portal_profile_context(student)
    ctx["password_form"] = password_form
    return render(request, "easylearn/portal_profile.html", ctx)


class PortalPasswordChangeView(PasswordChangeView):
    form_class = PortalPasswordChangeForm
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Su contraseña se actualizó correctamente.")
        return response


@login_required
def edit_profile(request):
    student = request.user
    Profile.objects.get_or_create(student=student)
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
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("profile")
        messages.error(request, "Revise los datos del formulario.")

    ctx = _portal_profile_context(student)
    ctx.update(
        {
            "student_update_form": student_update_form,
            "profile_edit_form": profile_edit_form,
        }
    )
    return render(request, "easylearn/portal_edit_profile.html", ctx)


@login_required
def design_system(request):
    if not settings.DEBUG:
        return HttpResponseNotFound()
    Profile.objects.get_or_create(student=request.user)
    return render(
        request,
        "easylearn/design_system.html",
        {"student": request.user, "portal_role_label": "Design system"},
    )


@login_required
@require_POST
def notifications_mark_read(request):
    nid = request.POST.get("id")
    mark_notifications_read(
        request.user,
        notification_id=int(nid) if nid and str(nid).isdigit() else None,
    )
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True})
    return redirect(request.META.get("HTTP_REFERER") or request.user.get_dashboard_url_name())


@login_required
def delete_account(request):
    student = request.user
    student.delete()
    request.session.flush()
    messages.success(request, "You have deleted your account successfully")
    return redirect("login")
