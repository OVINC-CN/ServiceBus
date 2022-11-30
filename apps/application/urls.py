from rest_framework.routers import DefaultRouter

from apps.application.views import ApplicationViewSet

router = DefaultRouter()
router.register("", ApplicationViewSet)

urlpatterns = router.urls
