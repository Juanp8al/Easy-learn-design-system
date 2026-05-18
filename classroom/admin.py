from django.contrib import admin

from classroom.models import (
    AcademicWeek,
    Activity,
    Announcement,
    Forum,
    Grade,
    StudyMaterial,
    Submission,
)


class StudyMaterialInline(admin.TabularInline):
    model = StudyMaterial
    extra = 0


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0


@admin.register(AcademicWeek)
class AcademicWeekAdmin(admin.ModelAdmin):
    list_display = ("offering", "week_number", "title", "status")
    list_filter = ("status", "offering__period")
    search_fields = ("title", "offering__code", "offering__name")
    inlines = [StudyMaterialInline, ActivityInline]


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "week", "material_type", "is_required", "published_at")
    list_filter = ("material_type",)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "week", "activity_type", "due_at", "status")
    list_filter = ("activity_type", "status")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("activity", "student", "status", "is_draft", "submitted_at")
    list_filter = ("status", "is_draft")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("submission", "score", "graded_by", "graded_at")
    list_filter = ("graded_at",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "offering", "week", "priority", "published_at")
    list_filter = ("priority",)


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ("title", "week", "status", "published_at")
    list_filter = ("status",)
