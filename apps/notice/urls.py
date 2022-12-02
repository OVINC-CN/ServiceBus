from rest_framework.routers import DefaultRouter

from apps.notice.views import NoticeViewSet

router = DefaultRouter()
router.register("", NoticeViewSet)

urlpatterns = router.urls
