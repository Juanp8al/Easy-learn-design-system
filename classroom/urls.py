from django.urls import path

from classroom import teacher_views, views

app_name = "classroom"

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("curso/<int:offering_id>/", views.course_detail, name="course_detail"),
    path(
        "curso/<int:offering_id>/semana/<int:week_number>/",
        views.week_detail,
        name="week_detail",
    ),
    path(
        "actividad/<int:activity_id>/entregar/",
        views.activity_submit,
        name="activity_submit",
    ),
    # Alias heredados
    path("curso/<int:offering_id>/entrar/", views.enter_offering, name="enter_offering"),
    path("semana/<int:week_id>/", views.enter_week, name="enter_week"),
    path("actividad/<int:activity_id>/", views.enter_activity, name="enter_activity"),
    path(
        "docente/curso/<int:offering_id>/",
        teacher_views.manage_course,
        name="teacher_manage_course",
    ),
    path(
        "docente/entrega/<int:submission_id>/calificar/",
        teacher_views.grade_submission,
        name="teacher_grade_submission",
    ),
    path(
        "docente/foro/<int:forum_id>/estado/",
        teacher_views.toggle_forum_status,
        name="teacher_toggle_forum",
    ),
]
