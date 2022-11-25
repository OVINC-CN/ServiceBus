from rest_framework.routers import DefaultRouter

from apps.account.views import UserInfoViewSet, UserPropertyViewSet, UserSignViewSet

router = DefaultRouter()
router.register("", UserSignViewSet)
router.register("user_info", UserInfoViewSet)
router.register("user_property", UserPropertyViewSet)

urlpatterns = router.urls
