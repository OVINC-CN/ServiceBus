from apps.iam.views.action import IAMActionViewSet
from apps.iam.views.instance import IAMInstanceAppViewSet, IAMInstanceViewSet
from apps.iam.views.user import UserPermissionViewSet

__all__ = [
    "IAMActionViewSet",
    "IAMInstanceAppViewSet",
    "IAMInstanceViewSet",
    "UserPermissionViewSet",
]
