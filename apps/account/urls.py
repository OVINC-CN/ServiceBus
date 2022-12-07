from rest_framework.routers import DefaultRouter

from apps.account.views import (
    UserInfoViewSet,
    UserPropertyViewSet,
    UserSearchViewSet,
    UserSignViewSet,
)

router = DefaultRouter()
router.register("", UserSignViewSet)
router.register("user_info", UserInfoViewSet)
router.register("user_property", UserPropertyViewSet)
router.register("user_search", UserSearchViewSet)

urlpatterns = router.urls
