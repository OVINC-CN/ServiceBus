from rest_framework.routers import DefaultRouter

from apps.cos.views import COSViewSet

router = DefaultRouter()
router.register("", COSViewSet)

urlpatterns = router.urls
