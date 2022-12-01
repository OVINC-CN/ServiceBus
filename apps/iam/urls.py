from rest_framework.routers import DefaultRouter

from apps.iam.views import (
    CheckPermissionViewSet,
    IAMActionViewSet,
    IAMInstanceAppViewSet,
    IAMInstanceViewSet,
    ManagerUserPermissionViewSet,
    UserPermissionViewSet,
)

router = DefaultRouter()
router.register("action", IAMActionViewSet)
router.register("instance", IAMInstanceViewSet)
router.register("instance_manage", IAMInstanceAppViewSet)
router.register("user", UserPermissionViewSet)
router.register("check", CheckPermissionViewSet)
router.register("manage", ManagerUserPermissionViewSet)

urlpatterns = router.urls
