# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from accounts.models import Student, Profile


@admin.register(Student)
class StudentAdmin(DjangoUserAdmin):
    list_display = DjangoUserAdmin.list_display + ("role",)
    list_filter = DjangoUserAdmin.list_filter + ("role",)
    ordering = ("username",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {"fields": ("role",)}),
        (
            "MER académico",
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
