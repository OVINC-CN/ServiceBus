from rest_framework.decorators import action
from rest_framework.response import Response

from apps.notice.constants import NoticeWayChoices
from apps.notice.models import NoticeLog
from apps.notice.serializers import MailRequestSerialzier, SmsRequestSerializer
from apps.notice.utils import NoticeBase
from core.auth import ApplicationAuthenticate
from core.viewsets import MainViewSet


class NoticeViewSet(MainViewSet):
    """
    Notice
    """

    queryset = NoticeLog.get_queryset()
    authentication_classes = [ApplicationAuthenticate]

    @action(methods=["POST"], detail=False)
    def mail(self, request, *args, **kwargs):
        """
        mail
        """

        # validate request
        request_serializer = MailRequestSerialzier(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # send
        NoticeBase.send_notice(NoticeWayChoices.MAIL.value, **request_data)
        return Response()

    @action(methods=["POST"], detail=False)
    def sms(self, request, *args, **kwargs):
        """
        sms
        """

        # validate request
        request_serializer = SmsRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # send
        NoticeBase.send_notice(NoticeWayChoices.MSG.value, **request_data)
        return Response()
