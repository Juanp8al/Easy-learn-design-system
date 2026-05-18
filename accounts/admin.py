# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from accounts.models import Profile, Student, UserNotification


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "title", "read_at", "created_at")
    list_filter = ("kind", "read_at")
    search_fields = ("title", "message", "user__username")


@admin.register(Student)
class StudentAdmin(DjangoUserAdmin):
    list_display = DjangoUserAdmin.list_display + ("role",)
    list_filter = DjangoUserAdmin.list_filter + ("role",)
    ordering = ("username",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {"fields": ("role",)}),
        (
            "Programa académico",
            {"fields": ("academic_program", "academic_semester")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "academic_program",
                    "academic_semester",
                ),
            },
        ),
    )


admin.site.register(Profile)
