from rest_framework.routers import DefaultRouter

from apps.home.views import HomeView

router = DefaultRouter()
router.register("", HomeView)

urlpatterns = router.urls
