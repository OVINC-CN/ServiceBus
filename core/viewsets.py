import traceback

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.logger import logger
from core.utils import get_ip


class MainViewSet(GenericViewSet):
    """
    Base ViewSet
    """

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)

        # Record Request
        try:

            if hasattr(request, "user") and hasattr(request.user, "username") and hasattr(request.user, "nick_name"):
                user = f"{request.user.username}({request.user.nick_name})"
            else:
                user = str(getattr(request, "user", ""))
            logger.info(
                "[RequestLog] User => %s; Path => %s:%s; Request => %s; Response => %s; Extras => %s",
                user,
                request.method,
                request.path,
                {"params": request.GET, "body": request.data},
                self.response.data if hasattr(self.response, "data") else self.response.content,
                {
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "ip": get_ip(request),
                    "referer": request.META.get("HTTP_REFERER", ""),
                },
            )

        except Exception:
            logger.error(traceback.format_exc())

        return self.response


class CreateMixin(mixins.CreateModelMixin):
    ...


class ListMixin(mixins.ListModelMixin):
    ...


class RetrieveMixin(mixins.RetrieveModelMixin):
    ...


class UpdateMixin(mixins.UpdateModelMixin):
    ...


class DestroyMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response()
