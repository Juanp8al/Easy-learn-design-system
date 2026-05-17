from django.contrib import admin

from .models import AcademicPeriod, Enrollment, Offering, Program


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    raw_id_fields = ("student",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "code", "slug")


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "starts_on", "ends_on", "is_current")
    list_filter = ("is_current",)


@admin.register(Offering)
class OfferingAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "program", "period", "semester", "group", "teacher", "credits")
    list_filter = ("period", "program")
    search_fields = ("name", "code", "teacher__username", "teacher__first_name", "teacher__last_name")
    raw_id_fields = ("teacher",)
    inlines = [EnrollmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "offering", "status", "enrolled_at")
    list_filter = ("status", "offering__period")
    raw_id_fields = ("student", "offering")
    search_fields = ("student__username", "student__first_name", "offering__code", "offering__name")
