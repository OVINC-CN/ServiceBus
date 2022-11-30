import abc

from django.utils.translation import gettext
from rest_framework.permissions import BasePermission

from apps.application.models import ApplicationManager
from apps.iam.models import Action
from core.exceptions import PermissionDenied


class ManagerPermissionBase(BasePermission):
    """
    Application Manager Permission
    """

    def has_permission(self, request, view):
        application = self._get_application_id(request)
        if ApplicationManager.objects.filter(application_id=application, manager=request.user).exists():
            return True
        raise PermissionDenied(gettext("Application Manager Permission Required"))

    @abc.abstractmethod
    def _get_application_id(self, request):
        ...


class ManageObjPermissionBase(BasePermission):
    """
    Application Manager Permission
    """

    def has_object_permission(self, request, view, obj):
        application = self._get_application_id(obj)
        if ApplicationManager.objects.filter(application_id=application, manager=request.user).exists():
            return True
        raise PermissionDenied(gettext("Application Manager Permission Required"))

    @abc.abstractmethod
    def _get_application_id(self, obj):
        ...


class IAMCreatePermission(ManagerPermissionBase):
    """
    Create IAM Permission
    """

    def _get_application_id(self, request):
        return request.data.get("application")


class IAMUpdatePermission(ManageObjPermissionBase):
    """
    Update IAM Permission
    """

    def _get_application_id(self, obj):
        return obj.application.app_code


class IAMActionAppPermission(BasePermission):
    """
    IAM Action App Permission
    """

    def has_permission(self, request, view):
        action = request.data.get("action", int())
        if Action.objects.filter(application=request.user, pk=action).exists():
            return True
        raise PermissionDenied(gettext("Unauthorized App for Action"))


class IAMActionObjAppPermission(BasePermission):
    """
    IAM Action Obj App Permission
    """

    def has_object_permission(self, request, view, obj):
        if obj.action.application == request.user:
            return True
        raise PermissionDenied(gettext("Unauthorized App for Action"))


class UserPermissionSelf(BasePermission):
    """
    Only User self can edit
    """

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        raise PermissionDenied(gettext("You are not allowed to update this permission"))
