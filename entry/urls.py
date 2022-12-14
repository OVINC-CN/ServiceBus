from django.conf import settings
from django.urls import include, path
from django.views.generic import RedirectView

from core import exceptions

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=f"{settings.FRONTEND_URL}/favicon.ico")),
    path("", include("apps.home.urls")),
    path("account/", include("apps.account.urls")),
    path("application/", include("apps.application.urls")),
    path("iam/", include("apps.iam.urls")),
    path("notice/", include("apps.notice.urls")),
    path("cos/", include("apps.cos.urls")),
]

handler400 = exceptions.bad_request
handler403 = exceptions.permission_denied
handler404 = exceptions.page_not_found
handler500 = exceptions.server_error
