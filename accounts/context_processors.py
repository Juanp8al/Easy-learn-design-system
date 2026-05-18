from accounts.notifications import get_portal_notifications


def portal_notifications(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    items, unread = get_portal_notifications(request.user)
    return {
        "portal_notifications": items,
        "portal_notifications_unread": unread,
    }
