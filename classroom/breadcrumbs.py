"""Migas de pan del aula con enlaces Django (no hash)."""

from django.urls import reverse


def _item(label, url_name=None, url_kwargs=None, url_hash=""):
    if url_name:
        return {
            "label": label,
            "url": reverse(url_name, kwargs=url_kwargs or {}) + url_hash,
        }
    return {"label": label, "url": None}


def student_home_crumbs():
    return [
        _item("Inicio", "notes:dashboard"),
        _item("Aula virtual", "classroom:course_list"),
    ]


def course_crumbs(offering):
    crumbs = student_home_crumbs()
    crumbs.append(_item(offering.name))
    return crumbs


def week_crumbs(offering, week):
    crumbs = course_crumbs(offering)
    crumbs[-1] = _item(offering.name, "classroom:course_detail", {"offering_id": offering.id})
    crumbs.append(_item(f"Semana {week.week_number}"))
    return crumbs


def activity_crumbs(offering, week, activity):
    crumbs = week_crumbs(offering, week)
    crumbs[-1] = _item(
        f"Semana {week.week_number}",
        "classroom:week_detail",
        {"offering_id": offering.id, "week_number": week.week_number},
    )
    crumbs.append(_item(activity.title))
    return crumbs
