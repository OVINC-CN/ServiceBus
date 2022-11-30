from django.utils.translation import gettext_lazy
from rest_framework.permissions import BasePermission

from apps.application.models import Application
from core.exceptions import PermissionDenied


class ApplicationAdminPermission(BasePermission):
    """
    Create or Delete Application
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        raise PermissionDenied(gettext_lazy("Admin Permission Required"))


class ApplicationManagePermission(BasePermission):
    """
    Update Application
    """

    def has_object_permission(self, request, view, obj: Application):
        # load managers
        managers = obj.applicationmanager_set.all().values_list("manager", flat=True)

        # check permission
        if request.user.username in managers:
            return True
        raise PermissionDenied(gettext_lazy("App Manager Permission Required"))
