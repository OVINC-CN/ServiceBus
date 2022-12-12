import abc

from django.utils.translation import gettext
from rest_framework.permissions import BasePermission

from apps.application.models import ApplicationManager
from apps.iam.exceptions import ActionDoesNotExist
from apps.iam.models import Action, UserPermission
from core.constants import ViewActionChoices
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


class ManagePermissionPermission(BasePermission):
    """
    Application Manager can manage permission
    """

    def has_permission(self, request, view):
        if view.action in [ViewActionChoices.LIST]:
            application_id = request.query_params.get("application_id")
            if ApplicationManager.objects.filter(application_id=application_id, manager=request.user).exists():
                return True
            raise PermissionDenied(gettext("Application Manager Permission Required"))
        if view.action in [ViewActionChoices.CREATE]:
            managed_apps = ApplicationManager.objects.filter(manager=request.user).values_list("application")
            actions = Action.objects.filter(application__in=managed_apps)
            if UserPermission.objects.filter(id=request.data.get("permission_id"), action__in=actions).exists():
                return True
            raise PermissionDenied(gettext("Application Manager Permission Required"))
        raise PermissionDenied()


class BulkSaveInstancePermission(BasePermission):
    """
    Bulk Save Instance Permission
    """

    def has_permission(self, request, view):
        action_ids = {instance["action_id"] for instance in request.data if instance.get("action_id")}
        actions = list(
            Action.objects.filter(id__in=action_ids, application=request.user).values_list("action_id", flat=True)
        )
        if len(action_ids) == len(actions):
            return True
        un_auth_action = list(set(action_ids) - set(actions))
        raise ActionDoesNotExist(gettext("Action Not Exist %s") % un_auth_action)
