"""Create and Manage Model Manager."""
from django.db.models import Manager
from django.db.models.query import QuerySet
from .generic import repos
from .constants import group_permissions


class IPQuerySet(QuerySet):
    """Create IP queryset manager to get specific record."""

    def for_user(self, user):
        """Method to get specific user permission records."""
        if repos.user_has_perm(user, group_permissions.IP_VIEW_ALL) or \
                repos.user_has_perm(user, group_permissions.IP_MANAGE_ALL):
            return self.all()
        elif repos.user_has_perm(user, group_permissions.IP_VIEW_OWN) or \
                repos.user_has_perm(user, group_permissions.IP_MANAGE_OWN):
            return self.filter(managers__in=[user])
        return self.none()

    def enabled(self):
        """Get the list of all enabled records."""
        return self.filter(disabled=False)

    def visible(self):
        """Get the list of all visible records."""
        return self.enabled().filter(hidden=False)

    def by_country(self, country):
        """Get the list records by country."""
        return self.filter(events__countries__country=country).distinct()

IPManager = Manager.from_queryset(IPQuerySet)
