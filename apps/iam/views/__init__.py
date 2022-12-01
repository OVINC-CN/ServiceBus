from apps.iam.views.action import IAMActionViewSet
from apps.iam.views.instance import IAMInstanceAppViewSet, IAMInstanceViewSet
from apps.iam.views.user import (
    CheckPermissionViewSet,
    ManagerUserPermissionViewSet,
    UserPermissionViewSet,
)

__all__ = [
    "IAMActionViewSet",
    "IAMInstanceAppViewSet",
    "IAMInstanceViewSet",
    "UserPermissionViewSet",
    "CheckPermissionViewSet",
    "ManagerUserPermissionViewSet",
]
